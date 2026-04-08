"""
Strategy 4: Guest Post Outreach
Discovers 'write for us' pages and sends outreach emails.
"""
import json
import os
import re
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

from core.http_client import get_session
from core.rate_limiter import delay, email_delay

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "guest_post_queries.json")
TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), "..", "templates", "guest_post_email.txt")

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def _render_email(config: dict, site_url: str) -> tuple[str, str]:
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        raw = f.read()
    b = config.get("business", {})
    replacements = {
        "{{business_name}}": b.get("name", ""),
        "{{website}}": b.get("website", ""),
        "{{tagline}}": b.get("tagline", ""),
        "{{sender_name}}": config.get("smtp", {}).get("from_name", b.get("name", "")),
        "{{site_url}}": site_url,
        "{{description}}": b.get("description", ""),
        "{{keywords}}": ", ".join(b.get("keywords", [])),
    }
    body = raw
    for k, v in replacements.items():
        body = body.replace(k, v)

    lines = body.splitlines()
    subject = lines[0].replace("Subject: ", "").strip() if lines else "Guest Post Opportunity"
    body = "\n".join(lines[1:]).strip()
    return subject, body


def _extract_emails(session, url: str) -> list[str]:
    emails = set()
    paths_to_check = ["", "/contact", "/contact-us", "/about", "/about-us"]
    base = url.rstrip("/")
    for path in paths_to_check:
        try:
            resp = session.get(base + path, timeout=10)
            if resp.status_code == 200:
                found = EMAIL_REGEX.findall(resp.text)
                for e in found:
                    if not any(x in e for x in ["example.com", "domain.com", "yoursite"]):
                        emails.add(e.lower())
        except Exception:
            pass
    return list(emails)


def discover_sites(config: dict, session) -> list[dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    queries = data.get("search_queries", [])
    seed_domains = data.get("seed_domains", [])
    contact_paths = data.get("contact_page_paths", ["/contact"])

    discovered = []

    # Check seed domains first
    for domain in seed_domains:
        emails = _extract_emails(session, domain)
        if emails:
            discovered.append({"url": domain, "emails": emails, "source": "seed"})

    # Google search for write-for-us pages
    try:
        from googlesearch import search
        for query in queries[:8]:  # limit to avoid rate limiting
            try:
                results = list(search(query, num_results=5, sleep_interval=3))
                for url in results:
                    if not any(d["url"] == url for d in discovered):
                        emails = _extract_emails(session, url)
                        if emails:
                            discovered.append({"url": url, "emails": emails, "source": "search"})
                delay(config)
            except Exception:
                pass
    except ImportError:
        print("[outreach] googlesearch-python not installed — using seed domains only")

    return discovered


def send_emails(sites: list[dict], config: dict, logger, dry_run: bool = False):
    smtp_cfg = config.get("smtp", {})
    done = logger.get_done_sites()

    for site in sites:
        url = site["url"]
        # Use domain as site_name for dedup
        domain = re.sub(r"https?://", "", url).split("/")[0]
        site_name = f"outreach:{domain}"

        if site_name in done:
            print(f"[outreach] Skipping {domain} — already emailed")
            continue

        subject, body = _render_email(config, url)

        for recipient_email in site.get("emails", []):
            if dry_run:
                print(f"\n[outreach] DRY RUN — would email: {recipient_email}")
                print(f"Subject: {subject}")
                print(f"Body preview: {body[:200]}...\n")
                logger.log({
                    "date": datetime.utcnow().isoformat(),
                    "strategy": "outreach",
                    "site_name": site_name,
                    "url_submitted": url,
                    "backlink_url": "",
                    "status": "skipped",
                    "notes": f"dry-run — would email {recipient_email}",
                })
                continue

            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{smtp_cfg.get('from_name', '')} <{smtp_cfg.get('from_email', '')}>"
                msg["To"] = recipient_email
                msg["Reply-To"] = smtp_cfg.get("reply_to", smtp_cfg.get("from_email", ""))
                msg.attach(MIMEText(body, "plain"))

                context = ssl.create_default_context()
                if smtp_cfg.get("use_ssl", True):
                    with smtplib.SMTP_SSL(smtp_cfg["host"], smtp_cfg.get("port", 465), context=context) as server:
                        server.login(smtp_cfg["username"], smtp_cfg["password"])
                        server.sendmail(smtp_cfg["from_email"], recipient_email, msg.as_string())
                else:
                    with smtplib.SMTP(smtp_cfg["host"], smtp_cfg.get("port", 587)) as server:
                        server.starttls(context=context)
                        server.login(smtp_cfg["username"], smtp_cfg["password"])
                        server.sendmail(smtp_cfg["from_email"], recipient_email, msg.as_string())

                logger.log({
                    "date": datetime.utcnow().isoformat(),
                    "strategy": "outreach",
                    "site_name": site_name,
                    "url_submitted": url,
                    "backlink_url": "",
                    "status": "pending",
                    "notes": f"Email sent to {recipient_email}",
                })
                print(f"[outreach] Email sent to {recipient_email} ({domain})")
                email_delay(config)

            except Exception as e:
                logger.log({
                    "date": datetime.utcnow().isoformat(),
                    "strategy": "outreach",
                    "site_name": site_name,
                    "url_submitted": url,
                    "backlink_url": "",
                    "status": "failed",
                    "notes": str(e),
                })
            break  # Only email the first valid address per site


def run(config: dict, logger, dry_run: bool = False, headed: bool = False):
    session = get_session(config)
    print("[outreach] Phase 1: Discovering guest post opportunities...")
    sites = discover_sites(config, session)
    print(f"[outreach] Found {len(sites)} sites with contact emails")
    print("[outreach] Phase 2: Sending outreach emails...")
    send_emails(sites, config, logger, dry_run=dry_run)
