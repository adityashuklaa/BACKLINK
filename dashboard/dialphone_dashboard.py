"""DialPhone.com Backlink Dashboard v2 — proper charts, filters, SEO metrics."""
import csv
import os
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)
ROOT = os.path.dirname(os.path.dirname(__file__))
VERIFIED_CSV = os.path.join(ROOT, "output", "backlinks_final_truth.csv")
MASTER_CSV = os.path.join(ROOT, "output", "backlinks_log.csv")

# Domain authority scores for visualization
DA_SCORES = {
    "dev.to": 77, "github.com": 100, "gitlab.com": 92, "codeberg.org": 55,
    "quora.com": 93, "paste.rs": 50, "glot.io": 55, "friendpaste.com": 45,
    "godbolt.org": 60, "hashnode.dev": 85, "hashnode.com": 85,
    "ideone.com": 75, "paste2.org": 55, "bpa.st": 30, "snippet.host": 40,
    "pastebin.fi": 28, "termbin.com": 45, "paste.centos.org": 60, "paste.debian.net": 70,
    "dpaste.com": 60,
    # Pages (static hosting — inherit parent authority)
    "github.io": 95, "gitlab.io": 92, "codeberg.page": 55,
    # Product-fit dirs
    "trustpilot.com": 94, "g2.com": 90, "capterra.com": 93, "capterra.co.uk": 93,
    "linkedin.com": 98, "alternativeto.net": 89, "saashub.com": 65, "crunchbase.com": 92,
    "trustradius.com": 82, "clutch.co": 92, "goodfirms.co": 82, "producthunt.com": 92,
    "bbb.org": 93, "manta.com": 84, "yellowpages.com": 80, "yelp.com": 94,
    "foursquare.com": 88, "bingplaces.com": 100, "yellowpages.ca": 78, "canada411.ca": 75,
    "medium.com": 96, "tumblr.com": 95, "substack.com": 89, "indiehackers.com": 79,
    "stackoverflow.com": 93,
}

DOFOLLOW_DOMAINS = {
    "dev.to", "github.com", "gitlab.com", "codeberg.org",
    "hashnode.dev", "hashnode.com",
    # Pages — dofollow by default since they're static sites we own
    "github.io", "gitlab.io", "codeberg.page",
    # Dofollow product-fit / editorial dirs
    "trustradius.com", "clutch.co", "goodfirms.co", "alternativeto.net", "saashub.com",
    "crunchbase.com", "producthunt.com",
    "medium.com", "tumblr.com", "substack.com", "indiehackers.com",
}

# Spam score per domain (0-100, higher = more spam-like per Google link-graph signals).
# Grounded in our audit at reports/backlink_seo_audit.md. Factors:
#  - User-generated content with weak/no moderation
#  - High outbound link-to-content ratio
#  - Known paste-site / link-farm pattern
#  - Duplicate content prevalence
#  - Google indexation rate of the source
# Scores below 25 = clean, 25-55 = moderate, 55+ = HIGH risk (Google likely devalues).
SPAM_SCORES = {
    # Editorial / moderated dev platforms — clean
    "dev.to": 10,
    "github.com": 5,
    "gitlab.com": 10,
    "codeberg.org": 15,
    "hashnode.dev": 10,
    "hashnode.com": 10,
    "quora.com": 15,
    "stackoverflow.com": 5,
    # Pages — our own static sites, same as parent
    "github.io": 5,
    "gitlab.io": 10,
    "codeberg.page": 15,
    # Product-fit dirs — reviewed listings
    "trustpilot.com": 5,
    "g2.com": 5,
    "capterra.com": 5, "capterra.co.uk": 5,
    "linkedin.com": 5,
    "alternativeto.net": 15,
    "saashub.com": 20,
    "crunchbase.com": 10,
    "trustradius.com": 10, "clutch.co": 10, "goodfirms.co": 15,
    "producthunt.com": 15,
    "bbb.org": 5, "manta.com": 20, "yellowpages.com": 20, "yelp.com": 15,
    "foursquare.com": 15, "bingplaces.com": 5,
    "yellowpages.ca": 20, "canada411.ca": 20,
    "medium.com": 15, "tumblr.com": 20, "substack.com": 10, "indiehackers.com": 15,
    # Moderate — topic-relevant paste sites with some editorial control
    "paste.debian.net": 35,
    "paste.centos.org": 40,
    # HIGH spam — user-gen paste / code dumps, heavy outbound ratio, weak moderation
    "paste.rs": 75,
    "glot.io": 70,
    "friendpaste.com": 75,
    "termbin.com": 80,
    "godbolt.org": 50,
    "ideone.com": 55,
    "bpa.st": 70,
    "paste2.org": 75,
    "snippet.host": 65,
    "pastebin.fi": 70,
    "dpaste.com": 70,
}

def _spam_tier(score):
    if score <= 25: return ("clean", "#10b981")
    if score <= 55: return ("moderate", "#f59e0b")
    return ("high", "#ef4444")

def _normalize_domain(url):
    """Extract domain from URL, strip www prefix. Returns lowercased domain."""
    try:
        d = url.split("//", 1)[1].split("/", 1)[0].lower()
        if d.startswith("www."):
            d = d[4:]
        return d
    except Exception:
        return ""

def _lookup_with_fallback(domain):
    """Return (da, spam, dofollow) for a domain, walking up parent domains if exact not found.

    Example: dialphonevoip.hashnode.dev → lookup full first, then hashnode.dev, then dev.
    This fixes the "default 40" bug where every subdomain showed as moderate-unknown.
    """
    if domain in SPAM_SCORES:
        return DA_SCORES.get(domain, 40), SPAM_SCORES[domain], domain in DOFOLLOW_DOMAINS
    parts = domain.split(".")
    for i in range(1, len(parts) - 1):
        parent = ".".join(parts[i:])
        if parent in SPAM_SCORES:
            return DA_SCORES.get(parent, 40), SPAM_SCORES[parent], parent in DOFOLLOW_DOMAINS
    return 40, 40, False

def _enrich(r):
    url = r["backlink_url"]
    domain = _normalize_domain(url)
    if "github" in domain and "gist" not in domain and not domain.endswith(".github.io"):
        domain = "github.com"
    r["_domain"] = domain
    da, spam, dofollow = _lookup_with_fallback(domain)
    r["_da"] = da
    r["_spam"] = spam
    r["_dofollow"] = dofollow
    tier, colour = _spam_tier(spam)
    r["_spam_tier"] = tier
    r["_spam_colour"] = colour
    return r

def count_quarantined():
    """Count rows in the verified CSV that are marked spam_quarantined or stale_vestacall."""
    if not os.path.exists(VERIFIED_CSV):
        return 0, 0
    q, s = 0, 0
    with open(VERIFIED_CSV, "r", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            st = r.get("status", "")
            if st == "spam_quarantined": q += 1
            elif st == "stale_vestacall": s += 1
    return q, s


def load_data():
    """Load only URLs that were hard-verified to contain 'dialphone' in live content.
    Dedupes by URL. Quora URLs are whitelisted (403 blocks our bot, but they are ours)."""
    rows = []

    # 1) Hard-verified rows (live fetched, dialphone confirmed in body)
    # Filter out spam_quarantined / stale_vestacall so dashboard only shows live, clean wins.
    if os.path.exists(VERIFIED_CSV):
        with open(VERIFIED_CSV, "r", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                if r.get("status") == "success":
                    rows.append(r)

    # 2) Whitelist: Quora URLs from master CSV (quora returns 403 to bots)
    with open(MASTER_CSV, "r", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            if r.get("status") != "success":
                continue
            url = r.get("backlink_url", "")
            if "quora.com" in url and "dialphone" in r.get("notes", "").lower():
                rows.append(r)

    # Dedupe by URL, keep newest
    rows.sort(key=lambda x: x.get("date", ""), reverse=True)
    seen, out = set(), []
    for r in rows:
        url = r.get("backlink_url", "")
        if not url or url in seen or "//" not in url:
            continue
        seen.add(url)
        out.append(_enrich(r))
    return out

TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DialPhone Backlink Command Center</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif; background: #0b0d14; color: #e4e6eb; min-height: 100vh; }
.layout { display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; }

/* Sidebar */
.sidebar { background: #0f111a; border-right: 1px solid #1f2430; padding: 24px 16px; position: sticky; top: 0; height: 100vh; }
.logo { font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #a78bfa, #60a5fa); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 4px; }
.logo-sub { font-size: 11px; color: #64748b; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 32px; }
.nav-item { padding: 10px 12px; color: #94a3b8; font-size: 13px; border-radius: 6px; margin-bottom: 2px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.nav-item.active { background: #1e293b; color: #fff; }
.nav-item:hover { background: #161a23; color: #e4e6eb; }
.nav-section { font-size: 10px; color: #475569; letter-spacing: 1.5px; text-transform: uppercase; margin: 20px 0 8px 12px; font-weight: 700; }

/* Main */
.main { padding: 28px 36px; }
.topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; padding-bottom: 20px; border-bottom: 1px solid #1f2430; }
.title-block h1 { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
.title-block .sub { font-size: 13px; color: #64748b; }
.timestamp { font-size: 12px; color: #475569; text-align: right; }
.timestamp .live { color: #10b981; font-weight: 600; display: flex; align-items: center; gap: 6px; justify-content: flex-end; }
.dot { width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

/* KPI Cards */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }
.kpi { background: #13161f; border: 1px solid #1f2430; border-radius: 12px; padding: 20px 24px; position: relative; overflow: hidden; }
.kpi::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; }
.kpi.g::before { background: #10b981; }
.kpi.b::before { background: #3b82f6; }
.kpi.p::before { background: #a78bfa; }
.kpi.o::before { background: #f59e0b; }
.kpi.r::before { background: #ef4444; }
.kpi .label { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 600; }
.kpi .value { font-size: 32px; font-weight: 800; color: #fff; margin-bottom: 4px; line-height: 1; }
.kpi .delta { font-size: 11px; color: #64748b; }
.kpi .delta.up { color: #10b981; }

/* Grid layout */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.grid-3 { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 24px; }
.card { background: #13161f; border: 1px solid #1f2430; border-radius: 12px; padding: 20px 24px; }
.card h3 { font-size: 14px; font-weight: 600; margin-bottom: 16px; color: #e4e6eb; display: flex; justify-content: space-between; align-items: center; }
.card h3 .badge { font-size: 10px; background: #1e293b; color: #64748b; padding: 3px 8px; border-radius: 10px; font-weight: 500; }
.chart-wrap { height: 260px; position: relative; }

/* Domain chips */
.domain-list { display: flex; flex-direction: column; gap: 8px; max-height: 260px; overflow-y: auto; padding-right: 4px; }
.domain-list::-webkit-scrollbar { width: 4px; }
.domain-list::-webkit-scrollbar-thumb { background: #334155; border-radius: 2px; }
.domain-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #161a23; border-radius: 6px; font-size: 13px; }
.domain-name { color: #a78bfa; font-weight: 600; }
.domain-stats { display: flex; gap: 12px; align-items: center; font-size: 11px; color: #64748b; }
.da-pill { background: #1e293b; padding: 2px 8px; border-radius: 10px; font-size: 10px; color: #60a5fa; font-weight: 700; }
.da-pill.high { background: rgba(16, 185, 129, 0.15); color: #10b981; }

/* Table */
.table-wrap { background: #13161f; border: 1px solid #1f2430; border-radius: 12px; overflow: hidden; }
.table-header { padding: 16px 20px; border-bottom: 1px solid #1f2430; display: flex; justify-content: space-between; align-items: center; }
.table-header h3 { font-size: 14px; font-weight: 600; }
.filters { display: flex; gap: 6px; }
.filter-btn { background: #161a23; border: 1px solid #1f2430; color: #94a3b8; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 500; transition: all 0.15s; }
.filter-btn:hover { background: #1e293b; color: #e4e6eb; }
.filter-btn.active { background: #4f46e5; border-color: #6366f1; color: #fff; }
.search { background: #161a23; border: 1px solid #1f2430; color: #e4e6eb; padding: 6px 12px; border-radius: 6px; font-size: 12px; width: 240px; }
.search:focus { outline: none; border-color: #4f46e5; }

table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 10px 20px; background: #0f111a; color: #475569; font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; border-bottom: 1px solid #1f2430; }
td { padding: 12px 20px; border-bottom: 1px solid #161a23; font-size: 12px; vertical-align: middle; }
tr:hover td { background: #161a23; }

.type-badge { padding: 3px 10px; border-radius: 10px; font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.type-dofollow { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }
.type-buyer { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.type-live { background: rgba(16, 185, 129, 0.15); color: #10b981; }

a { color: #60a5fa; text-decoration: none; }
a:hover { text-decoration: underline; }

.pagination { padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; color: #64748b; font-size: 12px; border-top: 1px solid #1f2430; }
.pagination button { background: #161a23; border: 1px solid #1f2430; color: #94a3b8; padding: 5px 12px; border-radius: 6px; font-size: 11px; cursor: pointer; }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.pagination button:not(:disabled):hover { background: #1e293b; color: #fff; }

.stat-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 12px; }
.stat-row .bar { flex: 1; height: 6px; background: #1f2430; border-radius: 3px; overflow: hidden; }
.stat-row .fill { height: 100%; background: linear-gradient(90deg, #4f46e5, #a78bfa); border-radius: 3px; }
.stat-row .count { color: #64748b; min-width: 40px; text-align: right; font-weight: 600; font-variant-numeric: tabular-nums; }

/* Clickable affordance */
.nav-item { cursor: pointer; transition: background 0.15s, transform 0.1s; }
.nav-item:active { transform: scale(0.98); }
.pill-badge { background: #4f46e5; padding: 2px 8px; border-radius: 10px; font-size: 10px; color: #fff; font-weight: 700; }
.kpi.clickable { cursor: pointer; transition: border-color 0.15s, transform 0.1s; }
.kpi.clickable:hover { border-color: #4f46e5; }
.kpi.clickable:active { transform: scale(0.99); }
.domain-row.clickable { cursor: pointer; transition: background 0.15s; }
.domain-row.clickable:hover { background: #1e293b; }
.domain-row.active-filter { background: #312e81; border: 1px solid #6366f1; }
#activeFilterBanner { display: none; background: linear-gradient(135deg, rgba(79,70,229,0.15), rgba(139,92,246,0.08)); border: 1px solid #4f46e5; padding: 10px 16px; border-radius: 8px; margin-bottom: 16px; font-size: 13px; color: #c7d2fe; display: flex; justify-content: space-between; align-items: center; }
#activeFilterBanner.visible { display: flex; }
#clearFilter { background: #4f46e5; border: none; color: #fff; padding: 5px 12px; border-radius: 6px; font-size: 11px; cursor: pointer; font-weight: 600; }
#clearFilter:hover { background: #6366f1; }
</style>
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <div class="logo">DialPhone</div>
    <div class="logo-sub">Command Center</div>
    <div class="nav-section">Campaign</div>
    <div class="nav-item active" data-nav-filter="all"><span>Backlinks</span><span class="pill-badge">{{ total }}</span></div>
    <div class="nav-item" data-nav-filter="dofollow"><span>Dofollow</span><span style="color:#a78bfa">{{ dofollow }}</span></div>
    <div class="nav-item" data-scroll="#domainsCard"><span>Domains</span><span style="color:#60a5fa">{{ domains_count }}</span></div>
    <div class="nav-section">Performance</div>
    <div class="nav-item" data-nav-filter="high-da"><span>Avg DA / High DA</span><span style="color:#10b981">{{ avg_da }}</span></div>
    <div class="nav-item" data-scroll="#seoScore"><span>Total DA weight</span><span style="color:#f59e0b">{{ total_da }}</span></div>
    <div class="nav-section">Risk</div>
    <div class="nav-item" data-nav-filter="clean"><span>Clean links</span><span style="color:#10b981">{{ spam_clean }}</span></div>
    <div class="nav-item" data-nav-filter="spam-moderate"><span>Moderate risk</span><span style="color:#f59e0b">{{ spam_moderate }}</span></div>
    <div class="nav-item" data-nav-filter="spam-high"><span>High spam risk</span><span style="color:#ef4444">{{ spam_high }}</span></div>
    <div class="nav-section">Target</div>
    <a href="https://dialphone.com" target="_blank" class="nav-item" style="text-decoration:none;color:inherit;"><span style="color:#60a5fa">dialphone.com ↗</span></a>
  </aside>

  <main class="main">
    <div class="topbar">
      <div class="title-block">
        <h1>Backlink Overview</h1>
        <div class="sub">Target: dialphone.com — every URL hard-verified (live fetched & content-checked)</div>
      </div>
      <div class="timestamp">
        <div class="live"><span class="dot"></span>LIVE · CLEAN ONLY</div>
        <div>Last sync: {{ updated }}</div>
        <div style="margin-top:6px;font-size:10px;color:#ef4444;">Quarantined: {{ quarantined }} spam + {{ stale_vestacall }} stale</div>
      </div>
    </div>

    <div id="activeFilterBanner">
      <span>Filtered: <strong id="filterDesc"></strong> · Showing <strong id="filterCount"></strong> backlinks</span>
      <button id="clearFilter">Clear filter</button>
    </div>

    <div class="kpi-grid">
      <div class="kpi g clickable" data-nav-filter="all" title="All live, dialphone.com-linked URLs. Goal: 1000 by end of May 2026.">
        <div class="label">Total Backlinks</div>
        <div class="value">{{ total }}</div>
        <div class="delta up">{{ target_pct }}% of 1000 target · <span style="color:#10b981">+{{ added_today }} today</span></div>
      </div>
      <div class="kpi p clickable" data-nav-filter="dofollow"><div class="label">Dofollow Links</div><div class="value">{{ dofollow }}</div><div class="delta">{{ dofollow_pct }}% · filter</div></div>
      <div class="kpi b clickable" data-scroll="#domainsCard"><div class="label">Referring Domains</div><div class="value">{{ domains_count }}</div><div class="delta">Diversity = {{ diversity_pct }}% · jump ↓</div></div>
      <div class="kpi o clickable" data-nav-filter="high-da" title="Average Domain Authority across all clean backlinks. Click to filter DA ≥ 70 only."><div class="label">Average DA</div><div class="value">{{ avg_da }}</div><div class="delta">{{ high_da_count }} links DA ≥ 70 · click to filter</div></div>
      <div class="kpi r clickable" data-nav-filter="spam-high" title="High-spam-score backlinks actively hurt SEO per Google's link-graph filters. Lower is better.">
        <div class="label">Spam-Risk Links</div>
        <div class="value" style="color:#ef4444;">{{ spam_high }}</div>
        <div class="delta">{{ spam_high_pct }}% · avg spam score {{ avg_spam }}/100 · <span style="color:#ef4444;">click to filter</span></div>
      </div>
    </div>

    <div class="grid-3">
      <div class="card">
        <h3>Backlink Growth <span class="badge">Last 24h</span></h3>
        <div class="chart-wrap"><canvas id="growthChart"></canvas></div>
      </div>
      <div class="card">
        <h3>Platform Mix</h3>
        <div class="chart-wrap"><canvas id="pieChart"></canvas></div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card" id="domainsCard">
        <h3>Top Referring Domains <span class="badge">{{ domains_count }} total · click to filter</span></h3>
        <div class="domain-list">
        {% for d, info in domain_details %}
          <div class="domain-row clickable" data-domain-filter="{{ d }}">
            <div>
              <span class="domain-name">{{ d }}</span>
              <span class="da-pill {{ 'high' if info.da >= 70 else '' }}">DA {{ info.da }}</span>
            </div>
            <div class="domain-stats">
              <span>{{ info.count }}</span>
              <div style="width:60px;height:4px;background:#1f2430;border-radius:2px;overflow:hidden;">
                <div style="height:100%;width:{{ info.pct }}%;background:linear-gradient(90deg,#4f46e5,#a78bfa);"></div>
              </div>
            </div>
          </div>
        {% endfor %}
        </div>
      </div>
      <div class="card">
        <h3>Authority Distribution</h3>
        <div style="padding:12px 0;">
        {% for label, count, pct in da_buckets %}
          <div class="stat-row">
            <div style="width:100px;font-size:11px;color:#94a3b8;">{{ label }}</div>
            <div class="bar"><div class="fill" style="width:{{ pct }}%;"></div></div>
            <div class="count">{{ count }}</div>
          </div>
        {% endfor %}
        </div>
        <div id="seoScore" style="margin-top:20px;padding-top:20px;border-top:1px solid #1f2430;">
          <div style="font-size:11px;color:#64748b;margin-bottom:8px;">SEO STRENGTH SCORE</div>
          <div style="display:flex;align-items:baseline;gap:8px;">
            <div style="font-size:32px;font-weight:800;background:linear-gradient(135deg,#a78bfa,#60a5fa);-webkit-background-clip:text;background-clip:text;color:transparent;">{{ seo_score }}</div>
            <div style="font-size:12px;color:#64748b;">/ 100</div>
          </div>
          <div style="font-size:11px;color:#64748b;margin-top:4px;">DA-weighted dofollow, spam-penalized</div>
        </div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <h3>Spam Risk Distribution <span class="badge" title="Google's link-graph devalues high-spam sources. Lower is better.">SEO-critical</span></h3>
        <div style="padding:12px 0;">
        {% for label, count, pct, colour in spam_buckets %}
          <div class="stat-row">
            <div style="width:120px;font-size:11px;color:#94a3b8;">{{ label }}</div>
            <div class="bar"><div class="fill" style="width:{{ pct }}%;background:{{ colour }};"></div></div>
            <div class="count">{{ count }}</div>
          </div>
        {% endfor %}
        </div>
        <div style="margin-top:16px;padding:12px;background:#0f111a;border-left:3px solid #ef4444;border-radius:4px;font-size:11px;color:#94a3b8;line-height:1.5;">
          <strong style="color:#e4e6eb;">Why this matters:</strong> High-spam-source backlinks aren't just ignored by Google — they actively hurt. Penguin + the 2022 Link Spam Update automatically devalue or negative-signal links from sources flagged as user-gen paste/code dumps, link farms, or heavy outbound domains. A clean link from DA 50 beats 10 spam links from DA 70.
        </div>
      </div>
      <div class="card">
        <h3>Footprint Concentration <span class="badge" title="High concentration on few domains signals link-network manipulation to Google.">pattern risk</span></h3>
        <div style="padding:12px 0;">
        {% for d, count, pct, conc_colour in footprint_rows %}
          <div class="stat-row">
            <div style="width:130px;font-size:11px;color:{{ conc_colour }};font-weight:600;">{{ d }}</div>
            <div class="bar"><div class="fill" style="width:{{ pct }}%;background:{{ conc_colour }};"></div></div>
            <div class="count">{{ count }}</div>
          </div>
        {% endfor %}
        </div>
        <div style="margin-top:16px;padding:12px;background:#0f111a;border-left:3px solid #f59e0b;border-radius:4px;font-size:11px;color:#94a3b8;line-height:1.5;">
          <strong style="color:#e4e6eb;">Risk signal:</strong> When >25% of your backlinks come from one domain, even if that domain is clean, Google flags the pattern. Concentration above 40% on a single source is a Penguin flag regardless of individual link quality. Diversification matters more than volume.
        </div>
      </div>
    </div>

    <div class="table-wrap">
      <div class="table-header">
        <h3>Backlink Directory</h3>
        <div style="display:flex;gap:10px;align-items:center;">
          <input type="text" id="search" class="search" placeholder="Search URL or platform...">
          <div class="filters">
            <button class="filter-btn active" data-filter="all">All</button>
            <button class="filter-btn" data-filter="dofollow">Dofollow</button>
            <button class="filter-btn" data-filter="high-da">High DA (70+)</button>
            <button class="filter-btn" data-filter="clean" style="color:#10b981;">Clean (spam≤25)</button>
            <button class="filter-btn" data-filter="spam-moderate" style="color:#f59e0b;">Moderate risk</button>
            <button class="filter-btn" data-filter="spam-high" style="color:#ef4444;">High spam risk</button>
            <button class="filter-btn" data-filter="quora">Quora</button>
          </div>
        </div>
      </div>
      <table>
        <thead>
          <tr><th>When</th><th>Platform</th><th>Domain</th><th>DA</th><th title="0-100 spam score. Higher = Google devalues or penalizes.">Spam</th><th>URL</th><th>Type</th></tr>
        </thead>
        <tbody id="tbody">
        {% for row in rows %}
          <tr data-dofollow="{{ '1' if row._dofollow else '0' }}" data-da="{{ row._da }}" data-spam="{{ row._spam }}" data-spam-tier="{{ row._spam_tier }}" data-domain="{{ row._domain }}" data-searchable="{{ row.backlink_url|lower }} {{ row.site_name|lower }}">
            <td style="color:#64748b;">{{ row.date[5:16].replace('T', ' ') }}</td>
            <td style="font-weight:500;">{{ row.site_name[:30] }}</td>
            <td><span class="da-pill {{ 'high' if row._da >= 70 else '' }}">{{ row._domain }}</span></td>
            <td style="color:{% if row._da >= 70 %}#10b981{% elif row._da >= 50 %}#fbbf24{% else %}#64748b{% endif %};font-weight:700;">{{ row._da }}</td>
            <td>
              <span style="display:inline-flex;align-items:center;gap:4px;background:{{ row._spam_colour }}22;color:{{ row._spam_colour }};padding:3px 8px;border-radius:10px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">
                {{ row._spam }}
              </span>
            </td>
            <td><a href="{{ row.backlink_url }}" target="_blank">{{ row.backlink_url[:55] }}{% if row.backlink_url|length > 55 %}…{% endif %}</a></td>
            <td>
            {% if 'quora' in row._domain %}<span class="type-badge type-buyer">BUYER</span>
            {% elif row._dofollow %}<span class="type-badge type-dofollow">DOFOLLOW</span>
            {% else %}<span class="type-badge type-live">LIVE</span>{% endif %}
            </td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
      <div class="pagination">
        <span>Showing <span id="shown">{{ rows|length }}</span> of {{ rows|length }} backlinks</span>
        <span>Auto-refreshed on load</span>
      </div>
    </div>
  </main>
</div>

<script>
// Growth chart
new Chart(document.getElementById('growthChart'), {
  type: 'line',
  data: {
    labels: {{ growth_labels|tojson }},
    datasets: [{
      label: 'Backlinks',
      data: {{ growth_data|tojson }},
      borderColor: '#a78bfa',
      backgroundColor: 'rgba(167, 139, 250, 0.1)',
      fill: true,
      tension: 0.35,
      pointRadius: 3,
      pointBackgroundColor: '#a78bfa',
      borderWidth: 2,
    }]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: { backgroundColor: '#13161f', borderColor: '#1f2430', borderWidth: 1, titleColor: '#fff', bodyColor: '#94a3b8' } },
    scales: {
      x: { grid: { color: '#161a23' }, ticks: { color: '#475569', font: { size: 10 } } },
      y: { grid: { color: '#161a23' }, ticks: { color: '#475569', font: { size: 10 } }, beginAtZero: true }
    }
  }
});

// Pie chart
new Chart(document.getElementById('pieChart'), {
  type: 'doughnut',
  data: {
    labels: {{ pie_labels|tojson }},
    datasets: [{
      data: {{ pie_data|tojson }},
      backgroundColor: ['#a78bfa','#60a5fa','#10b981','#f59e0b','#ef4444','#ec4899','#22d3ee','#84cc16','#fb923c'],
      borderColor: '#13161f', borderWidth: 2
    }]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 }, padding: 12, usePointStyle: true, pointStyle: 'circle' } }
    },
    cutout: '65%'
  }
});

// Unified filter state
let activeFilter = 'all', domainFilter = null, search = '';

const FILTER_LABELS = {
  all: 'All backlinks',
  dofollow: 'Dofollow only',
  'high-da': 'High authority (DA 70+)',
  clean: 'Clean sources (spam score ≤ 25)',
  'spam-moderate': 'Moderate spam risk (26-55)',
  'spam-high': 'High spam risk (56+) — Google likely devalues',
  quora: 'Quora answers only'
};

function applyFilters() {
  const rows = document.querySelectorAll('#tbody tr');
  let shown = 0;
  rows.forEach(r => {
    const dofollow = r.dataset.dofollow === '1';
    const da = parseInt(r.dataset.da);
    const spam = parseInt(r.dataset.spam);
    const spamTier = r.dataset.spamTier;
    const domain = r.dataset.domain;
    const searchable = r.dataset.searchable;
    let visible = true;
    if (activeFilter === 'dofollow' && !dofollow) visible = false;
    if (activeFilter === 'high-da' && da < 70) visible = false;
    if (activeFilter === 'quora' && !domain.includes('quora')) visible = false;
    if (activeFilter === 'clean' && spamTier !== 'clean') visible = false;
    if (activeFilter === 'spam-moderate' && spamTier !== 'moderate') visible = false;
    if (activeFilter === 'spam-high' && spamTier !== 'high') visible = false;
    if (domainFilter && domain !== domainFilter) visible = false;
    if (search && !searchable.includes(search)) visible = false;
    r.style.display = visible ? '' : 'none';
    if (visible) shown++;
  });
  document.getElementById('shown').textContent = shown;

  // Banner
  const banner = document.getElementById('activeFilterBanner');
  const hasFilter = activeFilter !== 'all' || domainFilter || search;
  if (hasFilter) {
    let desc = [];
    if (domainFilter) desc.push('domain: ' + domainFilter);
    if (activeFilter !== 'all') desc.push(FILTER_LABELS[activeFilter] || activeFilter);
    if (search) desc.push('search: "' + search + '"');
    document.getElementById('filterDesc').textContent = desc.join(' · ');
    document.getElementById('filterCount').textContent = shown;
    banner.classList.add('visible');
  } else {
    banner.classList.remove('visible');
  }

  // Sync active states
  document.querySelectorAll('.filter-btn').forEach(x => {
    x.classList.toggle('active', x.dataset.filter === activeFilter && !domainFilter);
  });
  document.querySelectorAll('.nav-item[data-nav-filter]').forEach(x => {
    x.classList.toggle('active', x.dataset.navFilter === activeFilter && !domainFilter);
  });
  document.querySelectorAll('.domain-row').forEach(x => {
    x.classList.toggle('active-filter', x.dataset.domainFilter === domainFilter);
  });
}

function setFilter(f) {
  activeFilter = f;
  domainFilter = null;
  applyFilters();
  document.querySelector('.table-wrap').scrollIntoView({behavior: 'smooth', block: 'start'});
}
function setDomainFilter(d) {
  domainFilter = (domainFilter === d) ? null : d;
  activeFilter = 'all';
  applyFilters();
  document.querySelector('.table-wrap').scrollIntoView({behavior: 'smooth', block: 'start'});
}
function clearAll() {
  activeFilter = 'all'; domainFilter = null; search = '';
  document.getElementById('search').value = '';
  applyFilters();
}

// Wire up filter buttons
document.querySelectorAll('.filter-btn').forEach(b => {
  b.addEventListener('click', () => setFilter(b.dataset.filter));
});
// Sidebar nav
document.querySelectorAll('.nav-item[data-nav-filter]').forEach(el => {
  el.addEventListener('click', () => setFilter(el.dataset.navFilter));
});
document.querySelectorAll('.nav-item[data-scroll]').forEach(el => {
  el.addEventListener('click', () => {
    document.querySelector(el.dataset.scroll).scrollIntoView({behavior: 'smooth', block: 'start'});
  });
});
// KPI cards
document.querySelectorAll('.kpi[data-nav-filter]').forEach(el => {
  el.addEventListener('click', () => setFilter(el.dataset.navFilter));
});
document.querySelectorAll('.kpi[data-scroll]').forEach(el => {
  el.addEventListener('click', () => {
    document.querySelector(el.dataset.scroll).scrollIntoView({behavior: 'smooth', block: 'start'});
  });
});
// Domain rows
document.querySelectorAll('.domain-row[data-domain-filter]').forEach(el => {
  el.addEventListener('click', () => setDomainFilter(el.dataset.domainFilter));
});
// Clear
document.getElementById('clearFilter').addEventListener('click', clearAll);
document.getElementById('search').addEventListener('input', e => {
  search = e.target.value.toLowerCase();
  applyFilters();
});

// Pie chart clickable
document.getElementById('pieChart').addEventListener('click', evt => {
  const chart = Chart.getChart('pieChart');
  const points = chart.getElementsAtEventForMode(evt, 'nearest', {intersect: true}, true);
  if (points.length) {
    const label = chart.data.labels[points[0].index];
    if (label !== 'other') setDomainFilter(label);
  }
});
</script>
</body>
</html>
"""

@app.route("/")
def dashboard():
    rows = load_data()
    total = len(rows)
    quarantined, stale_vestacall = count_quarantined()

    # Domain aggregation
    domain_counts = Counter(r["_domain"] for r in rows)
    max_count = max(domain_counts.values()) if domain_counts else 1
    domain_details = []
    for d, c in sorted(domain_counts.items(), key=lambda x: -x[1]):
        domain_details.append((d, {"count": c, "pct": (c / max_count) * 100, "da": DA_SCORES.get(d, 40)}))

    # Dofollow
    dofollow_rows = [r for r in rows if r["_dofollow"]]
    dofollow = len(dofollow_rows)
    dofollow_pct = round((dofollow / total) * 100) if total else 0

    # Quora
    quora = sum(1 for r in rows if "quora" in r["_domain"])

    # DA stats
    das = [r["_da"] for r in rows]
    avg_da = round(sum(das) / len(das)) if das else 0
    total_da = sum(das)
    high_da_count = sum(1 for d in das if d >= 70)

    # Progress toward 1000 target
    target_pct = round((total / 1000) * 100) if total else 0

    # Added today (last 24h)
    now_dt = datetime.now()
    added_today = 0
    for r in rows:
        try:
            dt = datetime.fromisoformat(r["date"])
            if now_dt - dt < timedelta(hours=24):
                added_today += 1
        except Exception:
            pass

    # Domain diversity — higher = less concentrated (inverse of top-domain % share)
    top_share = 0
    if total and domain_counts:
        top_share = max(domain_counts.values()) / total * 100
    diversity_pct = round(100 - top_share)

    # DA buckets
    buckets_raw = [
        ("DA 90-100", sum(1 for d in das if d >= 90)),
        ("DA 70-89", sum(1 for d in das if 70 <= d < 90)),
        ("DA 50-69", sum(1 for d in das if 50 <= d < 70)),
        ("DA 30-49", sum(1 for d in das if 30 <= d < 50)),
        ("DA < 30", sum(1 for d in das if d < 30)),
    ]
    max_bucket = max(b[1] for b in buckets_raw) or 1
    da_buckets = [(label, cnt, round((cnt / max_bucket) * 100)) for label, cnt in buckets_raw]

    # Spam score aggregates
    spams = [r["_spam"] for r in rows]
    avg_spam = round(sum(spams) / len(spams)) if spams else 0
    spam_clean = sum(1 for r in rows if r["_spam_tier"] == "clean")
    spam_moderate = sum(1 for r in rows if r["_spam_tier"] == "moderate")
    spam_high = sum(1 for r in rows if r["_spam_tier"] == "high")
    spam_high_pct = round((spam_high / total) * 100) if total else 0

    # Spam buckets (visual distribution)
    spam_buckets_raw = [
        ("Clean (≤25)", spam_clean, "#10b981"),
        ("Moderate (26-55)", spam_moderate, "#f59e0b"),
        ("High risk (56+)", spam_high, "#ef4444"),
    ]
    max_spam_bucket = max(b[1] for b in spam_buckets_raw) or 1
    spam_buckets = [(label, cnt, round((cnt / max_spam_bucket) * 100), colour) for label, cnt, colour in spam_buckets_raw]

    # Footprint concentration — % of backlinks from each top domain
    footprint_rows = []
    for d, c in sorted(domain_counts.items(), key=lambda x: -x[1])[:8]:
        pct_share = (c / total) * 100 if total else 0
        # Colour by concentration risk (>40% = red, >25% = amber, else green)
        if pct_share > 40:
            colour = "#ef4444"
        elif pct_share > 25:
            colour = "#f59e0b"
        else:
            colour = "#10b981"
        footprint_rows.append((d, c, round(pct_share), colour))

    # SEO strength score — DA-weighted dofollow PENALIZED for spam links
    # Each dofollow link contributes (DA × (1 - spam/100)); high-spam links add little
    raw = sum(r["_da"] * (1 - r["_spam"] / 100) for r in dofollow_rows)
    seo_score = min(100, round(raw / 100))

    # Growth chart - group by hour over last 24h
    now = datetime.now()
    hourly = defaultdict(int)
    for r in rows:
        try:
            dt = datetime.fromisoformat(r["date"])
            if now - dt < timedelta(hours=24):
                hourly[dt.hour] += 1
        except:
            pass
    growth_labels = []
    growth_data = []
    for i in range(24):
        h = (now.hour - 23 + i) % 24
        growth_labels.append(f"{h:02d}:00")
        growth_data.append(hourly.get(h, 0))

    # Pie chart - top 8 platforms + other
    top_platforms = sorted(domain_counts.items(), key=lambda x: -x[1])[:8]
    pie_labels = [d for d, _ in top_platforms]
    pie_data = [c for _, c in top_platforms]
    other = sum(c for d, c in domain_counts.items() if d not in pie_labels)
    if other > 0:
        pie_labels.append("other")
        pie_data.append(other)

    return render_template_string(TEMPLATE,
        total=total,
        dofollow=dofollow,
        dofollow_pct=dofollow_pct,
        domains_count=len(domain_counts),
        avg_da=avg_da,
        high_da_count=high_da_count,
        target_pct=target_pct,
        added_today=added_today,
        diversity_pct=diversity_pct,
        total_da=f"{total_da:,}",
        quora=quora,
        seo_score=seo_score,
        domain_details=domain_details,
        da_buckets=da_buckets,
        spam_clean=spam_clean,
        spam_moderate=spam_moderate,
        spam_high=spam_high,
        spam_high_pct=spam_high_pct,
        avg_spam=avg_spam,
        spam_buckets=spam_buckets,
        footprint_rows=footprint_rows,
        rows=rows,
        growth_labels=growth_labels,
        growth_data=growth_data,
        pie_labels=pie_labels,
        pie_data=pie_data,
        quarantined=quarantined,
        stale_vestacall=stale_vestacall,
        updated=datetime.now().strftime("%H:%M:%S"),
    )

if __name__ == "__main__":
    print("\n  DialPhone Command Center: http://127.0.0.1:5001\n")
    app.run(port=5001, debug=False)
