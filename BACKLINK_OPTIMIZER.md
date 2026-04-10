---
name: BACKLINK_OPTIMIZER
description: Deep code, performance, and efficiency analyzer for VestaCall backlink automation project
applyTo:
  - "**/*.py"
  - "{main,test}*.py"
  - "strategies/**/*.py"
  - "core/**/*.py"
restrictToolUse: []
tags:
  - backlink
  - optimization
  - efficiency
  - performance
  - detection-avoidance
---

# BACKLINK_OPTIMIZER — Interactive Deep Review Skill

**Activation**: `@copilot /BACKLINK_OPTIMIZER analyze <file_or_strategy>`  
**Purpose**: Provide comprehensive, prioritized recommendations to improve code quality, performance, detection avoidance, output quality, and team efficiency.

---

## How to Use This Skill

### Command Patterns

```
@copilot /BACKLINK_OPTIMIZER analyze social_bookmarking
@copilot /BACKLINK_OPTIMIZER audit main.py
@copilot /BACKLINK_OPTIMIZER team efficiency
@copilot /BACKLINK_OPTIMIZER detect risks strategies/
@copilot /BACKLINK_OPTIMIZER parallelize workflow
```

### What You Get
- ✅ Prioritized recommendations (CRITICAL, IMPORTANT, NICE-TO-HAVE)
- ✅ Specific code locations and examples
- ✅ Implementation effort estimates (quick, medium, involved)
- ✅ Impact on: detection avoidance, performance, code quality, team efficiency, output quality
- ✅ Success metrics (how to measure improvement)
- ✅ Next steps (actionable checklist)

---

## Analysis Dimensions

### 1. **Code Quality & Best Practices**

When analyzing a file, check:

- **Docstrings & Documentation**
  - [ ] Module has docstring explaining purpose?
  - [ ] Functions >5 lines have docstrings (what, args, returns, raises)?
  - [ ] Docstrings include rate limit strategy if applicable?
  - [ ] Constants have inline comments?
  - **Flag**: Any function without docstring → IMPORTANT.

- **Type Hints**
  - [ ] Function signatures have type hints?
  - [ ] Return types meaningful (not Any)?
  - [ ] Complex types (List, Dict, Optional) used correctly?
  - **Flag**: Missing type hints in public functions → IMPORTANT.

- **Error Handling**
  - [ ] Specific exceptions caught (not bare `except`)?
  - [ ] Custom exceptions from `core.exceptions`?
  - [ ] Error messages provide context?
  - [ ] Network errors (timeout, DNS, SSL) handled separately?
  - **Flag**: Bare except or silent failures → CRITICAL.

- **DRY & Reusability**
  - [ ] Rate limiting delegated to `core.rate_limiter`?
  - [ ] Browser automation delegated to `core.browser`?
  - [ ] HTTP requests use `core.http_client`?
  - [ ] CSV logging uses `core.csv_logger`?
  - [ ] No duplicated logic across strategies?
  - **Flag**: Duplicated rate limiting or logging code → IMPORTANT.

### 2. **Detection Avoidance & Security**

When analyzing a file, check:

- **Rate Limiting & Delays**
  - [ ] Every submission followed by `rate_limiter.wait(min=3, max=8)`?
  - [ ] Delays are randomized (not fixed 5s)?
  - [ ] No hardcoded `time.sleep()` without randomization?
  - [ ] Between-strategy delays included (e.g., 60s pause between strategies)?
  - [ ] If strategy makes API calls, validated against platform rate limits?
  - **Flag**: Missing or fixed delays → CRITICAL.

- **Browser & User-Agent Rotation**
  - [ ] Playwright browser launched with anti-detection config?
  - [ ] User-agent rotated per HTTP request?
  - [ ] Referer header included in HTTP requests (matching target domain)?
  - [ ] No browser context reused across unrelated batch submissions?
  - [ ] If using cookies, session isolated per user/account combination?
  - **Flag**: Static user-agent or no referer → CRITICAL.

- **IP & Session Management**
  - [ ] If proxy used, rotated between submissions?
  - [ ] No >10 submissions/hour to same domain on same IP?
  - [ ] Browser session rotated daily or per-campaign?
  - [ ] Failed submission (429 rate limit) triggers pause, not immediate retry?
  - **Flag**: No session rotation or retry-on-429 → CRITICAL.

- **Input Validation**
  - [ ] URLs validated before submission?
  - [ ] Emails validated before SMTP send?
  - [ ] Config values (SMTP, API keys) checked at startup?
  - **Flag**: Unvalidated user input → IMPORTANT.

### 3. **Performance & Efficiency**

When analyzing a file, check:

- **Runtime vs. Baselines**
  - Check actual runtime against expected (see `.instructions.md` section IV):
    - Directories: 3–5 min for 20 sites
    - Social Bookmarking: 5–8 min for 8 platforms
    - Forum Profiles: 10–15 min for 5+ forums
    - Guest Outreach: 8–12 min for 20 emails
    - Blog Comments: 6–10 min for 10 blogs
  - [ ] If strategy exceeds baseline by >20%, investigate bottleneck.
  - **Flag**: >20% above baseline → IMPORTANT.

- **Parallelization Opportunities**
  - [ ] Can multiple strategies run simultaneously (e.g., Directories + Social Bookmarking)?
  - [ ] Can browser contexts be reused/pooled across strategies?
  - [ ] Can CSV log be pre-loaded instead of checked per-submission?
  - [ ] Can API calls (Reddit, etc.) be batched?
  - **Flag**: Sequential strategies where parallelization possible → IMPORTANT.

- **CSV Logging Overhead**
  - [ ] CSV load time on startup (should be <1s for typical log size)?
  - [ ] Is CSV appended per submission (efficient) or re-read+rewritten?
  - [ ] Deduplication check O(1) via in-memory dict, not O(n) via CSV rescan?
  - **Flag**: CSV loaded on every submission or re-read → IMPORTANT.

- **Resource Usage**
  - [ ] Browser memory usage monitored? (Each Playwright instance ~100–200MB)
  - [ ] If parallelizing, do ≥2 browser instances fit in available memory?
  - [ ] HTTP connections pooled (reused across requests)?
  - [ ] File handles closed after CSV writes?
  - **Flag**: Unbounded browser creation or file handle leaks → IMPORTANT.

### 4. **Output Quality & Auditing**

When analyzing a file, check:

- **CSV Logging Completeness**
  - [ ] Every submission attempt logged to CSV (success, skip, failure)?
  - [ ] Required columns present: timestamp, strategy, site_name, submission_url, backlink_url, status, notes?
  - [ ] Status values consistent: success, failed, skipped, rate_limited, auth_failed?
  - [ ] Notes field provides reason for failure (e.g., "Duplicate submission today", "Rate limited 60s", "Auth required")?
  - [ ] Timestamps in ISO 8601 format?
  - **Flag**: Missing status or notes → CRITICAL.

- **Deduplication Logic**
  - [ ] CSV pre-loaded at strategy start (dict by site_name)?
  - [ ] Check for duplicates today (same site, same strategy, today's date)?
  - [ ] Deduplication reason logged ("Already submitted today")?
  - [ ] Can user override dedup with --force-resubmit flag?
  - **Flag**: No deduplication or re-submitting duplicates → IMPORTANT.

- **Error Categorization**
  - [ ] Network errors vs. auth errors vs. duplicate vs. rate limit clearly distinguished?
  - [ ] Error count tracked (e.g., 3+ consecutive failures → pause strategy)?
  - [ ] First-time-fix errors logged separately (e.g., "Form field missing" vs. "Rate limited")?
  - **Flag**: All errors lumped as "failed" without reason → IMPORTANT.

- **Success Metrics**
  - [ ] Success rate tracked (% of submissions with status='success')?
  - [ ] Can measure success rate by: strategy, person, day, site?
  - [ ] Target ≥75%; current rate vs. target logged in summary?
  - **Flag**: No success rate calculation → IMPORTANT.

### 5. **Team Efficiency & Accountability**

When analyzing a file, check:

- **Ownership & Responsibility**
  - [ ] Is it clear who owns this strategy? (Check `.instructions.md` Appendix)
  - [ ] Can submissions be attributed to a person (via CSV log or config)?
  - [ ] Blockers surfaced (e.g., "Yelp email verification required" blocks directory submissions)?
  - **Flag**: No ownership or blocker tracking → IMPORTANT.

- **Progress & Observability**
  - [ ] Progress printed to console every N submissions (N ≤ 5)?
  - [ ] ETA calculated and updated (e.g., "4/20 sites, ~45s remaining")?
  - [ ] Execution time logged at end (strategy took 4m 32s)?
  - [ ] If exceeds baseline, alert logged?
  - **Flag**: Silent execution with no progress feedback → IMPORTANT.

- **Metrics Tracking**
  - [ ] CSV log includes person/owner identifier?
  - [ ] Can calculate: submissions/person/week, success rate by person, runtime variance?
  - [ ] Weekly summary can be generated automatically?
  - **Flag**: No per-person tracking → IMPORTANT.

- **Dry-Run & Sand boxing**
  - [ ] Dry-run mode available (simulate submissions without sending)?
  - [ ] Dry-run prints what would be submitted (URL, email, post)?
  - [ ] Can compare dry-run results to CSV log for accuracy?
  - **Flag**: No dry-run mode → NICE-TO-HAVE.

---

## Recommendation Priorities

### CRITICAL (Fix Immediately)
- Detection avoidance weakened (rate limiting removed, delays fixed, static user-agents)
- Unlogged submissions (not added to CSV)
- Bare exception handlers (masking errors)
- Unvalidated input (security risk)
- Re-identification risk (browser session leaks identity)

### IMPORTANT (Fix This Week)
- Missing docstrings in public functions
- Missing type hints in function signatures
- Duplicated logic not extracted to `core/`
- CSV loaded on every submission (performance)
- Runtime >20% above baseline (investigate)
- No success rate tracking
- Errors not categorized (all lumped as "failed")

### NICE-TO-HAVE (Consider for Next Release)
- Dry-run mode enhancement (interactive preview)
- Progress bar improvement (ETA calculation)
- Parallelization of independent strategies
- Browser context pooling for memory efficiency
- Weekly efficiency report automation

---

## Analysis Workflow

### Step 1: Intake
When user requests analysis, identify scope:
- **Single strategy** (e.g., `/BACKLINK_OPTIMIZER analyze social_bookmarking`)
- **Multiple files** (e.g., `/BACKLINK_OPTIMIZER audit strategies/`)
- **Workflow/Main** (e.g., `/BACKLINK_OPTIMIZER parallelize workflow`)
- **Team metrics** (e.g., `/BACKLINK_OPTIMIZER team efficiency`)

### Step 2: Scan for Patterns
For each file:
1. **Detection avoidance**: Search for `time.sleep()`, `rate_limiter`, delays, user-agent rotation, randomization, proxy usage.
2. **Code quality**: Check function signatures, docstrings, error handling, try/except blocks, logging.
3. **Performance**: Measure expected runtime vs. actual, identify I/O bottlenecks, check CSV reloads.
4. **Output quality**: Verify CSV logging, error categorization, deduplication.
5. **Team efficiency**: Check for progress output, success rate calculation, ownership tracking.

### Step 3: Deep Dive (Per Dimension)
For each finding, provide:
- **Issue**: What's the problem? (specific code location or pattern)
- **Why it matters**: Impact on project (e.g., "Detection risk: static UA is bot signature")
- **Recommendation**: How to fix (code snippet or pattern)
- **Effort**: How long to fix (quick <5min, medium 15–30min, involved >1 hour)
- **Validation**: How to verify fix works (test case, metric, manual check)

### Step 4: Prioritize & Output
- **Group by priority**: CRITICAL, IMPORTANT, NICE-TO-HAVE
- **Sort by effort**: Quick wins first (fix in 5 min, big impact)
- **Check dependencies**: If fix A depends on fix B, note order
- **Provide summary**: Total issues, quick wins available, effort to resolve all

### Step 5: Suggest Next Steps
- "Start with: Fix bare excepts → add specific exception handling (15 min, CRITICAL)"
- "Then: Verify rate limiting delays are randomized (5 min, CRITICAL)"
- "Then: Extract duplicated rate limiting to core/rate_limiter.py (20 min, IMPORTANT)"
- "Finally: Add progress output and success rate tracking (30 min, IMPORTANT)"

---

## Example Analysis Output

```
BACKLINK_OPTIMIZER Analysis: strategies/social_bookmarking.py
================================================================

📊 OVERVIEW
- File: strategies/social_bookmarking.py (245 lines)
- Detection Risk: 🔴 HIGH (2 CRITICAL findings)
- Code Quality: 🟡 MEDIUM (4 IMPORTANT findings)
- Performance: 🟢 GOOD (on baseline)
- Team Tracking: 🟡 MEDIUM (1 IMPORTANT finding)

🚨 CRITICAL ISSUES (Fix Now)
────────────────────────────
1. DETECTION RISK: Line 87 — Bare time.sleep(5) without randomization
   Issue: Fixed 5s delay is bot-like signature; easily detected
   Fix: replace with rate_limiter.wait(min=3, max=8)
   Effort: Quick (3 min)
   Impact: Avoid IP ban on Reddit, Diigo

2. UNLOGGED SUBMISSION: Line 145 — Reddit post submitted without CSV log
   Issue: Submission success not recorded; breaks deduplication
   Fix: Add csv_logger.log_submission(...) call after successful post
   Effort: Quick (5 min)
   Impact: Prevent duplicate submissions; enable tracking

🟠 IMPORTANT ISSUES (Fix This Week)
──────────────────────────────────
3. MISSING DOCSTRING: Line 52 — Function `submit_to_reddit()` undocumented
   Issue: No docstring; unclear what strategy is used (OAuth vs. API)
   Fix: Add docstring explaining auth method, rate limit, expected runtime
   Effort: Quick (5 min)

4. CSV PRE-LOAD: Line 31 — CSV reloaded in loop for every platform
   Issue: CSV loaded 8x per run (once per platform); O(n) overhead
   Fix: Pre-load CSV at strategy start; check in O(1) per platform
   Effort: Medium (20 min)
   Impact: ~30% speed improvement (5→3.5 min runtime)

5. NO PROGRESS OUTPUT: Strategy runs silently; no feedback
   Issue: User doesn't know if it's working (especially for Diigo, Pocket with slow loads)
   Fix: Print every platform: "Posting to Reddit... OK (34s)"
   Effort: Quick (10 min)

6. NO SUCCESS RATE TRACKING: Can't measure strategy effectiveness
   Issue: Don't know which platforms fail most; can't optimize
   Fix: Track success_count/total_count; log final "8/8 posted successfully"
   Effort: Medium (15 min)

✅ QUICK WINS (Do First)
──────────────────────
- Fix bare sleep() with randomization (3 min) + Add CSV logging (5 min) = 8 min, +2 CRITICAL fixed
- Add function docstring (5 min)
- Add progress output (10 min)

Total Effort to Fix All: ~75 min

🔍 VALIDATION
─────────────
After fixes:
1. Run in dry-run mode; verify 8 submissions logged to CSV with status, notes
2. Check runtime: should be 5–8 min (don't allow <5s fixed delays)
3. Manually review CSV log: timestamps, URLs, backlinks all present
4. Run twice back-to-back; verify 2nd run skips all sites (deduplication works)

📋 NEXT STEPS
─────────────
[ ] Fix bare sleep() → randomize delays (3 min) — CRITICAL
[ ] Add CSV logging to Reddit post (5 min) — CRITICAL
[ ] Add function docstring (5 min) — IMPORTANT
[ ] Pre-load CSV at strategy start (20 min) — IMPORTANT
[ ] Add progress output loop (10 min) — IMPORTANT
[ ] Add success rate calculation (15 min) — IMPORTANT

After above, this strategy will be 80% optimized. Remaining 20% is parallelization (run with directories strategy in parallel).
```

---

## Common Patterns to Look For

### Detection Red Flags
```python
# 🚨 BAD: Fixed delay
time.sleep(5)

# ✅ GOOD: Randomized delay via core utility
from core.rate_limiter import wait
wait(min=3, max=8)
```

```python
# 🚨 BAD: Static user-agent
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# ✅ GOOD: Rotated user-agent
from core.http_client import get_random_user_agent, get_random_referer
headers = {
    'User-Agent': get_random_user_agent(),
    'Referer': get_random_referer(domain='reddit.com')
}
```

### Logging Red Flags
```python
# 🚨 BAD: No logging
response = submit_to_site(url)
if response.ok:
    print("Submitted!")

# ✅ GOOD: Logged to CSV
response = submit_to_site(url)
if response.ok:
    csv_logger.log_submission(
        strategy='directories',
        site_name='Yelp',
        submission_url=url,
        backlink_url=backlink_url,
        status='success',
        notes='Submitted form, email verification pending'
    )
```

### Performance Red Flags
```python
# 🚨 BAD: CSV loaded per-site
for site in sites:
    existing = pd.read_csv('backlinks_log.csv')  # Loaded 20x!
    if site in existing['site_name'].values:
        continue

# ✅ GOOD: CSV pre-loaded
existing_sites = csv_logger.load_submitted_today(strategy='directories')
for site in sites:
    if site in existing_sites:
        continue
```

---

## Files This Skill Applies To

- `main.py` — Orchestration logic, parallelization opportunities
- `strategies/*.py` — Primary targets for all 5 dimensions
- `core/browser.py` — Detection flags, browser reuse
- `core/http_client.py` — User-agent rotation, referer headers
- `core/rate_limiter.py` — Randomization, effectiveness
- `core/csv_logger.py` — Completion, CSV schema
- `config.json` — Config validation, credential management

---

## Integration with `.instructions.md`

This skill operationalizes the challenge questions from `.instructions.md` section VII. When running analysis:

1. Load `.instructions.md` challenge questions for context
2. Apply each question to the file(s) being analyzed
3. Return detailed findings mapped to section II (best practices) and section VI (metrics)
4. Suggest fixes prioritized by `.instructions.md` appendix ownership and baseline targets

---

## How to Invoke via Copilot Chat

```
# Deep analysis of a single strategy
@copilot /BACKLINK_OPTIMIZER analyze social_bookmarking

# Audit all strategy files for common issues
@copilot /BACKLINK_OPTIMIZER audit strategies/

# Identify parallelization opportunities in main.py
@copilot /BACKLINK_OPTIMIZER parallelize workflow

# Detect detection-avoidance risks across codebase
@copilot /BACKLINK_OPTIMIZER detect risks strategies/

# Generate team efficiency metrics from CSV
@copilot /BACKLINK_OPTIMIZER team efficiency

# Check a specific file for compliance with .instructions.md
@copilot /BACKLINK_OPTIMIZER compliance check core/rate_limiter.py
```

---

## Maintenance & Updates

- **Review quarterly**: Check if baselines in `.instructions.md` section IV are still accurate; update if needed.
- **Update per new strategy**: When new strategy added, add to challenge questions and baseline expectations.
- **Sync with team**: Share findings with strategy owners; incorporate feedback into this skill's recommendations.

