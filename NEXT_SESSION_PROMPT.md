# Continuation Prompt for Backlink Automation System

## Context
You are continuing work on a backlink automation system for **dialphone.com** (DialPhone Limited — UK VoIP/business phone provider). The system is built in Python with Playwright for browser automation and parallel API publishing.

## Current State (as of April 16, 2026)
- **220 dialphone.com backlinks** across 9 referring domains
- **85 dofollow links** (66 Dev.to articles, 14 GitLab repos, 11 Codeberg repos, 1 GitHub Pages)
- **6 Quora buyer answers** targeting VoIP purchase questions
- **Parallel publisher** at `run_parallel_publish.py` — one command publishes to 8 platforms in 45 seconds
- All config in `config.json` (Dev.to API key, GitLab token, Codeberg credentials, Quora login)
- Dashboard at `dashboard/dialphone_dashboard.py` (port 5001)
- Competitor analysis at `reports/competitor_backlink_analysis.md`

## Critical Problems to Fix (Priority Order)

### 1. GitHub repos still link to vestacall.com (NOT dialphone.com)
The 11 GitHub repos under `dialphonelimited` still have old vestacall.com README content. They need to be updated to dialphone.com links via web UI (Playwright). This is urgent — these are DA 100 dofollow links pointing to the wrong site.

### 2. glot.io duplicate content
The same VoIP ROI calculator code snippet is posted ~40 times on glot.io. This looks like spam. Either vary the code content per post or stop publishing to glot.io.

### 3. Domain diversity is weak (9 domains, competitors have 20+)
29 platforms from the competitor list are unused. Priority platforms to add:
- Vercel (DA 92) — deploy static landing page
- Netlify (DA 90) — deploy static landing page  
- npmjs.com (DA 95) — publish a real micro-package
- CodePen (DA 93) — create VoIP calculator widget
- Crunchbase (DA 92) — submit company profile (manual)
- ProductHunt (DA 92) — launch product page (manual)
- Tumblr (DA 95) — blog posts (credentials in config.json)
- WordPress.com (DA 95) — blog posts
See `reports/competitor_backlink_analysis.md` for full list.

### 4. Too many paste site links (132 of 220 = 60%)
Paste sites are filler. They add backlink count but minimal SEO value. Stop running paste batches. Focus on:
- More Quora answers (buyer traffic)
- More Dev.to articles (dofollow, DA 77)
- New platform deploys (each = new referring domain)

### 5. Need buyer traffic NOW (not just SEO fuel)
Only Quora generates direct buyer clicks. Need to expand to:
- LinkedIn articles (via Ocoya at app.ocoya.com — user has account)
- Medium articles (need account)
- More Quora answers (target: 50+ across different questions)
- Reddit posts in r/sysadmin, r/VoIP, r/smallbusiness (careful — community moderated)

### 6. Old vestacall.com articles on Dev.to
58 articles from vestacall campaign still exist under `dialphonelimited` Dev.to account. Options:
- Leave them (they don't hurt dialphone.com but waste the account's authority)
- Dev.to doesn't allow bulk editing, so can't change them retroactively
- Focus on publishing more dialphone.com articles to dilute the vestacall ones

## System Architecture

### Key Files
- `run_parallel_publish.py` — main publisher (--api-only, --devto N, --gitlab, --verify, --stats)
- `run_quora.py` / `run_quora_batch.py` — Quora answer posting
- `run_code_platforms.py` — GitLab/Bitbucket/Codeberg API repos
- `run_deploy_platforms.py` — deploy to new platforms
- `core/content_engine.py` — DIALPHONE_MENTIONS array, get_random_mention()
- `core/browser.py` — Playwright stealth browser with profile rotation
- `config.json` — ALL credentials (Dev.to key, GitLab token, GitHub password, Quora login, etc.)
- `output/backlinks_log.csv` — master log of all backlinks
- `dashboard/dialphone_dashboard.py` — DialPhone-only dashboard on port 5001
- `data/articles_dialphone_*.json` — article content files (33 batches)
- `data/company_repos*.json` — repo README content
- `reports/competitor_backlink_analysis.md` — competitor URL analysis

### Credentials (in config.json)
- Dev.to API key: `uxv8YjB7oK9ybwmPCdh5gTsJ`
- GitLab token: in config.json api_keys.gitlab
- GitHub: dialphonelimited / in config.json
- Codeberg: dialphonelimited / in config.json
- Quora: commercial@dialphone.com / in run_quora.py

### What Works (100% reliable)
- Dev.to API publishing (66/66 articles verified)
- GitLab API repo creation and README updates
- Codeberg API repo creation and README updates
- paste.rs raw POST API
- godbolt.org shortener API
- friendpaste.com auto-form detection
- Parallel execution (ThreadPoolExecutor, 8 platforms, 45 seconds)

### What Doesn't Work
- GitHub Gists (CodeMirror editor blocks Playwright — 0/15 success)
- Platform signups via Playwright (CAPTCHA on all sites)
- Bitbucket API (deprecated endpoints, app password auth issues)
- Telegraph (server permanently down)
- Hashnode (403 Forbidden)
- dpaste.com (pastes expire after 24 hours)

## Recommended Next Steps
1. Fix GitHub repos (update READMEs to dialphone.com)
2. Deploy landing pages on Vercel/Netlify/Pages.dev (3 new DA 90+ domains in 30 min)
3. Post 20+ more Quora answers (buyer traffic, the only thing generating clicks NOW)
4. Create accounts on Tumblr/WordPress/Medium (need manual signup — CAPTCHA)
5. Use Ocoya for LinkedIn/Twitter social posts with dialphone.com links
6. Publish npm package (dialphone-sip-checker) for DA 95 backlink
7. Submit to Crunchbase/ProductHunt manually (DA 92 each)
8. Stop paste site spam — focus on quality over quantity
9. Vary glot.io content (different code snippets per post)
10. Monitor SEMrush/Ahrefs in 2-3 weeks for backlink appearance
