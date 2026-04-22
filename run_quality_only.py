"""Quality-only backlink run: Dev.to + GitLab + Codeberg. NO paste sites.
Per reports/backlink_seo_audit.md — paste sites are zero-value. This is what we actually publish going forward."""
import sys
import json
import time

# Import from the parallel publisher (reuses verified publish functions)
import run_parallel_publish as pp

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_quality_only.py <content.json> [--devto N] [--gitlab] [--codeberg]")
        sys.exit(1)

    content_path = sys.argv[1]
    devto_n = 5
    do_gitlab = "--gitlab" in sys.argv
    do_codeberg = "--codeberg" in sys.argv

    # Pull out --devto N
    for i, a in enumerate(sys.argv):
        if a == "--devto" and i + 1 < len(sys.argv):
            devto_n = int(sys.argv[i + 1])

    # Load content
    data = json.load(open(content_path, encoding="utf-8"))
    articles = data.get("articles", [])[:devto_n]
    print(f"\n=== QUALITY-ONLY RUN ===")
    print(f"Content: {content_path}")
    print(f"Dev.to articles: {len(articles)}")
    print(f"GitLab: {'yes' if do_gitlab else 'no'}")
    print(f"Codeberg: {'yes' if do_codeberg else 'no'}")
    print("=" * 40)

    # Override module-level DEVTO_ARTICLES so publish_devto picks up our batch
    pp.DEVTO_ARTICLES = articles

    results = {"devto": [], "gitlab": [], "codeberg": []}

    # Dev.to (has rate limit but validator gate is already wired in)
    if articles:
        t0 = time.time()
        print(f"\n[{time.strftime('%H:%M:%S')}] Dev.to starting...")
        results["devto"] = pp.publish_devto(articles)
        print(f"Dev.to done in {time.time()-t0:.1f}s")

    # GitLab
    if do_gitlab:
        t0 = time.time()
        print(f"\n[{time.strftime('%H:%M:%S')}] GitLab starting...")
        if hasattr(pp, "publish_gitlab"):
            results["gitlab"] = pp.publish_gitlab()
        print(f"GitLab done in {time.time()-t0:.1f}s")

    # Codeberg
    if do_codeberg:
        t0 = time.time()
        print(f"\n[{time.strftime('%H:%M:%S')}] Codeberg starting...")
        if hasattr(pp, "publish_codeberg"):
            results["codeberg"] = pp.publish_codeberg()
        print(f"Codeberg done in {time.time()-t0:.1f}s")

    # Summary
    print("\n=== SUMMARY ===")
    for k, v in results.items():
        ok = sum(1 for r in v if getattr(r, "verified", False))
        total = len(v)
        print(f"  {k}: {ok}/{total} verified")


if __name__ == "__main__":
    main()
