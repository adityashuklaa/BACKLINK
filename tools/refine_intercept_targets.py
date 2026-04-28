"""Post-process competitor_backlink_targets_v2.csv:
- Apply real DA estimates for sites we recognize but didn't have in KNOWN_DA
- Filter out competitor brand domains (mightycall, aircall, vxt, votacall, etc.)
- Filter out obvious off-topic false positives
- Re-score and re-rank
"""
import csv
import json
import sys
sys.stdout.reconfigure(encoding="utf-8")

# Real-world DA estimates (Moz / Ahrefs DR — best-known values)
REAL_DA = {
    "capterra.co.uk": 93, "capterra.in": 85, "capterra.co.za": 80, "capterra.co.nz": 80,
    "getapp.com": 87, "getapp.ie": 80,
    "softwareadvice.com.au": 75, "softwareadvice.co.uk": 75,
    "technologyadvice.com": 70, "top10.com": 75,
    "me.pcmag.com": 88,  # PCMag MEA — inherits parent authority
    "sonary.com": 50, "founderjar.com": 50, "technewshaven.com": 45,
    "technologyforyou.org": 45, "topconsumerreviews.com": 65,
    "brightlio.com": 38, "onestopcomm.com": 35, "rigorousthemes.com": 50,
    "thevoiphub.com": 38, "bdtechsupport.com": 35, "isitwp.com": 70,
    "ifaxapp.com": 50, "phonesystemworld.com": 32,
    "startup.unitelvoice.com": 40, "smartreach.io": 50, "forssinc.com": 30,
    "topadvisor.com": 55, "messagedesk.com": 42, "techdator.net": 40,
    "courier.com": 65, "klenty.com": 55, "customerservicescoreboard.com": 45,
    "virtualhostedpbx.net": 40,
}

# Competitor brands — they won't link to us
COMPETITOR_BRANDS_TO_SKIP = {
    "aircall.io", "mightycall.com", "vxt.ai", "votacall.com", "blog.votacall.com",
    "openphone.com", "quo.com", "ringcentral.com", "8x8.com", "dialpad.com",
    "nextiva.com", "vonage.com", "goto.com", "zoom.us", "ooma.com",
    "grasshopper.com", "freshcaller.com", "cloudtalk.io",
}

# Off-topic false positives (junk we picked up)
OFF_TOPIC_DOMAINS = {
    "lebensversicherungkaufenprivat.info",  # German life insurance — false positive
    "customerservicescoreboard.com",  # CS scoreboard, weak fit
}


def rescore(da, relevance, mentions, links_competitor, text_length):
    """Same scoring formula as the main tool."""
    if not mentions: return 0
    if da < 35 or relevance < 4: return 0
    length_factor = min(1.0, text_length / 2000) if text_length else 0.3
    link_bonus = 8 if links_competitor else 0
    return round((da * 0.5) + (relevance * 4) + (length_factor * 10) + link_bonus, 1)


def main():
    rows = list(csv.DictReader(open("output/competitor_backlink_targets_v2.csv", encoding="utf-8")))
    print(f"input: {len(rows)} rows")

    refined = []
    skipped = {"competitor_brand": [], "off_topic": []}
    for r in rows:
        d = r["target_domain"]
        if d in COMPETITOR_BRANDS_TO_SKIP:
            skipped["competitor_brand"].append(d)
            continue
        if d in OFF_TOPIC_DOMAINS:
            skipped["off_topic"].append(d)
            continue
        # Update DA if we now know it
        if d in REAL_DA:
            new_da = REAL_DA[d]
            r["da_estimate"] = new_da
            r["da_source"] = "manual_real"
            # Re-score with new DA — assume length=2000 for max length factor
            links = "Links" in r["why_relevant"]
            new_roi = rescore(new_da, int(r["relevance_score"]), True, links, 2000)
            r["roi_score"] = new_roi
        refined.append(r)

    # Re-sort
    refined.sort(key=lambda r: -float(r["roi_score"]))

    # Write refined CSV
    fieldnames = list(rows[0].keys()) if rows else []
    with open("output/competitor_backlink_targets_v2_refined.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(refined)
    print(f"refined: {len(refined)} rows -> output/competitor_backlink_targets_v2_refined.csv")
    print(f"skipped competitor brands: {len(skipped['competitor_brand'])} ({skipped['competitor_brand']})")
    print(f"skipped off-topic: {len(skipped['off_topic'])} ({skipped['off_topic']})")

    # Print top 15 with real DAs
    print()
    print(f"{'#':>3}  {'DA':>3}  {'ROI':>5}  {'L':>1}  {'competitor':12s}  {'domain':35s}  title")
    print("-" * 130)
    for i, r in enumerate(refined[:20], 1):
        L = "L" if "Links" in r["why_relevant"] else "T"
        print(f"{i:>3}  {int(r['da_estimate']):>3}  {r['roi_score']:>5}  {L:>1}  {r['linked_competitor']:12s}  {r['target_domain'][:35]:35s}  {r['title'][:55]}")


if __name__ == "__main__":
    main()
