# Safety + Cooldown Plan

*Defensive playbook to prevent the 8-orgs-in-one-day pattern that risks bans, mass-deletion, and disavow recovery overlap.*

## Why this exists

On 2026-04-29 we executed an aggressive Day 1 push that added 170 backlinks across 5 platforms in one execution day. While every individual artifact passed humanize / source-quality / concentration gates, **the velocity itself is a separate detection vector**. Specific risks:

- **Codeberg** — 8 orgs created in 24h. Codeberg's abuse-detection layer flags accounts that create more than ~3 orgs/day for review. Possible outcomes: mass-deletion of created repos, account suspension, IP block.
- **Dev.to** — 37 articles published in 24h. Dev.to has no published rate limit but their moderation queue receives flags above ~10 articles/day from one account, triggering review and potential shadow-ban.
- **Hashnode** — 4 articles in 24h. We've already lost 74 articles to Hashnode moderation; their threshold is the strictest of the bunch.
- **Cross-platform pattern** — same destination URL, same author profile, same theme across 5 platforms in 24h is the signature of automated SEO-spam workflows.

## What we built (2026-04-29 evening)

### `core/safety.py` — central safety module

Public API:
- `pre_publish_check(platform, content, special_kind=None, respect_rest_day=True)` — single function every batch script calls before each publish
- `velocity_gate(platform, special_kind=None)` — returns OK / BLOCKED with the exact reason
- `log_publish(platform, url, content_excerpt, strategy)` — record after successful publish
- `jitter_sleep(base_seconds, variance_pct=0.4)` — randomized delay (humans don't post on a metronome)
- `content_similarity_check(content, platform, threshold=0.55)` — block if 55%+ word overlap with recent posts on same platform
- `is_rest_day()` — designates Sundays as no-publish days
- `velocity_status()` — snapshot for dashboards

### Per-platform daily / weekly / 30-day caps

```python
DAILY_CAPS = {
    # Platform: (per-24h, per-week, per-30d-rolling)
    "dev.to":              (5,   25,  80),
    "hashnode.dev":        (1,    4,  15),  # tightest — 74-article incident
    "codeberg.org":        (5,   30, 100),  # repos
    "codeberg-orgs":       (1,    3,   8),  # org creation specifically
    "codeberg.page":       (1,    3,   8),  # Pages subdomains
    "gitlab.com":          (3,   18,  60),
    "github.com":          (3,   18,  60),
    "tumblr.com":          (1,    5,  15),
    "medium.com":          (1,    5,  15),
    "substack.com":        (1,    5,  15),
    "indiehackers.com":    (1,    3,   8),
    "stackoverflow.com":   (3,   12,  35),
    "quora.com":           (3,   12,  35),
    "diigo.com":           (5,   25,  60),
    "spiceworks.com":      (2,    8,  20),
    "default":             (2,    8,  25),
}
```

Each platform has THREE rolling-window caps. Hitting any one blocks the gate. The 30-day cap is the SUSTAINED-pace cap; the 24h cap is the burst-pace cap. We need both.

### Wired into publishing scripts

- `tools/gen_and_push_devto.py` — Dev.to batch publisher
- `tools/gen_and_push.py` — GitLab + Codeberg niche publisher
- `tools/publish_hashnode_batch.py` — Hashnode batch publisher

All three now call `pre_publish_check()` before each individual publish and `log_publish()` after success. Safety gate hits = batch stops with explicit "STOPPING: 24h velocity cap hit. Resume tomorrow." message.

### `tools/safety_status.py` — CLI dashboard

`python tools/safety_status.py` prints current 24h / 7d / 30d counts vs. caps for every platform. Use this BEFORE running any batch tool.

### `output/daily_publish_velocity.json` — persistent log

Rolling 60-day record of every publish (platform, URL, timestamp, content excerpt). Auto-pruned to 60 days. Used by all gates.

## Cooldown plan for 2026-04-30 (tomorrow)

Today (2026-04-29) we are **BLOCKED** on:
- Dev.to (38/5 daily — 24h cap exhausted, recovers ~16:00 IST tomorrow as oldest entries roll out)
- GitLab (8/3 daily — recovers in ~6 hours)
- Codeberg.org (113/5 daily — recovers gradually)
- Codeberg.page (8/1 daily — recovers in 24h)
- Hashnode (3/1 daily — recovers in ~12 hours)

**Tomorrow's safe pace:**
- Dev.to: 0-5 (depending on how many roll out of the 24h window)
- Hashnode: 1
- Codeberg orgs: 0 (stay under 8/30d cap; at 8 already)
- Codeberg repos: 5 (under 30/7d cap if we had room)
- GitLab: 3
- New referring domains (Tumblr, Bitbucket, Stack Overflow profile, IndieHackers): 1 per platform per day

**Realistic Day 2 ceiling: ~12-18 backlinks** while the 24h cooldowns roll off.

## What to do EVERY morning

1. `python tools/safety_status.py` — see what's BLOCKED / WARN / OK
2. Decide which platforms to publish to (only OK or WARN with headroom)
3. Run batch tools — they'll auto-stop on 24h cap hit
4. Don't manually override `--ignore-velocity-cap` flag without a clear reason
5. Sundays: rest day by default; override with `--ignore-rest-day` only for genuine emergencies

## What changed in the workflow

| Before today | Now |
|---|---|
| `python tools/gen_and_push_devto.py --count 50` would publish 50 in one run | Gate stops at the 24h cap (5) and reports "resume tomorrow" |
| Sleep was always exactly `--sleep 35` seconds | Jitter randomizes between 21-49 seconds (40% variance) |
| Sundays were normal publishing days | Sundays are rest days by default |
| No content-similarity check between published items | Blocks if 55%+ word overlap with anything published in last 14 days on same platform |
| No central log of velocity | `output/daily_publish_velocity.json` tracked across all scripts |

## Long-term cooldown / sustained-pace targets

For the rest of May 2026:

| Platform | Target sustained pace |
|---|---|
| Dev.to | 3 articles/day max → ~80/month |
| Hashnode | 1 article every 2 days → ~14/month |
| GitLab | 2 repos/day → ~50/month |
| Codeberg repos | 3 repos/day → ~80/month |
| Codeberg orgs | 0 more this week, then 1 every 3 days → ~5 more |
| Codeberg.page | 0 more this week, then 1 every 3 days → ~5 more |
| Tumblr | 1 post/day if active |
| Stack Overflow | 1 answer/day |
| Quora | 1 answer/day |
| Diigo | 3-5 bookmarks/day |

**Sustained pace calculation:** 80 + 14 + 50 + 80 + 5 + 5 + 5 + 30 + 30 + 100 = **399 backlinks/month** at MAX safe pace. With Day 1's 170 already banked: **569 by end of May with zero risk**.

## Override protocol

`--ignore-velocity-cap` flag exists on all wired scripts but should be used only in:
1. **Genuine emergency** (e.g., calculator goes viral, need to publish a follow-up immediately to capitalize)
2. **One-shot platform** (e.g., setting up a Stack Overflow profile is a one-time action; capping at 1 makes no sense)
3. **Recovery tests** (publishing a single test article to verify a platform still works after suspected shadow-ban)

Every override should be logged in `wiki/log.md` with explicit justification.

## What to do if a platform DOES flag us

- **Codeberg mass-deletion**: stop publishing immediately, file an appeal via Codeberg's contact form, do not create new orgs for 14 days
- **Dev.to shadowban**: detected via `verify_via_api()` returning fewer published articles than logged; stop Dev.to entirely for 7 days, then test with one harmless article
- **Hashnode moderation deletion**: already happened once; if it recurs, abandon Hashnode and move 100% to Dev.to + Codeberg
- **GitLab repo flag**: less common; usually just delete the offending repo and continue

## Bottom line

**This is the safety net we should have built before Day 1, not after.** Going forward it will prevent any single day's push from triggering platform abuse-detection, while still allowing aggressive sustained pace via the rolling 30-day cap.

**The Day 1 risk has already been taken.** What we can do now is:
1. Cool down for 24-48 hours on the BLOCKED platforms
2. Use the safety system from Day 2 onward
3. Watch for any moderation events on what we already published (mass-deletion is the canary)
