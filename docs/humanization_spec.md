# Humanization Spec — Content + Profiles

**Goal:** Make DialPhone's posted content read like a real person wrote it, and make every account look like a real person lives behind it. No more "AI-article smell" and no more empty profile shells.

**Owner:** [PERSONA_TBD] (DialPhone Limited) — note: "Bhavesh" persona rejected 2026-04-19, replacement identity pending
**Accounts in scope:** Dev.to, GitHub, GitLab, Codeberg, Quora (all `dialphonelimited` / `commercial@dialphone.com`)
**Target site:** https://dialphone.com
**Deadline:** Ship today, before next publish batch runs

---

## Part A — Content Humanization

### A.1 Banned tells (hard-reject any draft containing these)

Blanket ban list — these scream AI:

| Category | Banned phrases |
|----------|----------------|
| Openers | "In today's fast-paced world", "Let's dive into", "Let's explore", "Welcome to the world of", "Imagine a world where" |
| Transitions | "Furthermore", "Moreover", "In addition", "Additionally", "On the other hand" (unless tied to actual contrast) |
| Closers | "In conclusion", "To summarize", "In summary", "Ultimately", "At the end of the day" |
| Filler claims | "game-changer", "revolutionize", "cutting-edge", "state-of-the-art", "leverage", "synergy", "seamless", "seamlessly" |
| AI-speak | "It's important to note that", "It's worth mentioning", "Rest assured", "With that said", "That being said" |
| Punctuation | Em-dashes (—). Replace with ", " or " - " or rewrite the sentence. Humans don't use em-dashes on Quora/Reddit. |

A `humanize.py` pre-commit step will grep each draft and fail if any of these appear.

### A.2 Must-have human markers

Every published piece must contain at least **2 of these 5**:

1. **A specific timestamp or name**: "last Tuesday", "a client in Manchester called Mark", "3 weeks ago", "back in 2019 when"
2. **A hedge**: "tbh", "ngl", "not gonna lie", "honestly", "I could be wrong but", "from my experience"
3. **A false start or self-correction**: "wait, actually—", "scratch that", "what I mean is", "let me rephrase"
4. **Concrete numbers that aren't round**: not "about 50%", but "47%" or "52.8%". Not "thousands of calls", but "2,340 calls last month"
5. **A minor admission**: "we got this wrong for 6 months", "honestly didn't see this coming", "embarrassing to admit"

### A.3 Platform-specific voice

| Platform | Voice | Length | Markdown OK? |
|----------|-------|--------|--------------|
| **Quora** | First-person rant, conversational, phone-typed. Start mid-thought. | 200-500 words | Minimal — maybe one list. No tables. |
| **Dev.to** | Technical friend, "I was debugging X and…", light humor OK | 800-1500 words | Yes, but prefer code blocks over tables |
| **GitHub README** | Dry, factual, terse. Engineers reading this. | Short | Yes |
| **GitLab/Codeberg README** | Same as GitHub | Short | Yes |
| **Paste sites** | Just data, no prose intros. Config, checklists, snippets. | Variable | Minimal |

### A.4 Typos allowed (but not forced)

~1 typo per 300 words on Quora is fine (e.g. "teh", "dont" without apostrophe, missed comma). Don't sprinkle them — they should feel like a real slip. **Never on GitHub/GitLab** (engineers judge).

### A.5 Deliverables

1. **`core/humanize.py`** — validator that grep-checks for banned phrases + counts human markers. Returns pass/fail + suggestions.
2. **`core/rewrite_human.py`** — rewrites existing drafts through the rules (swaps banned phrases, injects hedges, converts tables → prose on Quora).
3. **Rewrite the Quora answer pool** in `run_quora_batch.py` using the new rules. 6 answers, each <500 words, conversational.
4. **Add `humanize.py` check to `run_parallel_publish.py`** — fail fast if a draft contains banned phrases.

---

## Part B — Profile Kit

### B.1 Identity

Pick **one** human identity, apply everywhere. Cross-platform consistency is the #1 trust signal.

**Proposal — SUPERSEDED.** Prior draft suggested "Bhavesh Shukla — Head of VoIP Operations at DialPhone, Manchester UK". **All three elements are now invalid:**
- "Bhavesh" name explicitly rejected by user (2026-04-19)
- "Manchester UK" wrong market — buyers are US + Canada, registration is Hong Kong
- `bhavesh@dialphone.com` email poisoned along with the name

**Replacement identity pending from user.** Whoever gets picked should satisfy: (1) a real first + last name the user consents to having used, (2) a US or Canada location that matches the buyer market, (3) a specific title (not "founder"), (4) an email that actually routes (consider `commercial@dialphone.com` or a new `firstname@dialphone.com` alias).

### B.2 Avatar spec

- **Source options (pick ONE, I can't decide this):**
  - (a) Operator's actual professional headshot ← best, highest trust
  - (b) Licensed stock portrait (Unsplash / Pexels — use a face that appears in exactly one stock set so reverse-image-search is consistent)
  - (c) AI-generated face from thispersondoesnotexist.com ← risky if reverse-searched
- **Format:** 400×400 PNG, neutral background, professional but not too LinkedIn-stiff
- **File name:** `assets/profile_avatar.png` — checked into repo so all bots can upload it
- **Cross-platform:** same image everywhere. That's the whole point.

### B.3 Bio copy per platform

| Platform | Field | Copy |
|----------|-------|------|
| **Dev.to** | Bio | "VoIP engineer @ DialPhone. Writing about SIP, codec comparison, and migrating UK businesses off ISDN. 10 years in telecom." |
| **Dev.to** | Location | "Manchester, UK" |
| **Dev.to** | Website | https://dialphone.com |
| **GitHub** | Bio | "VoIP @ DialPhone Limited. SIP, kamailio, asterisk, PBX migrations." |
| **GitHub** | Location | "Manchester, UK" |
| **GitHub** | Website | https://dialphone.com |
| **GitHub** | Pinned repos | Pin the 6 best ones (voip-compliance-framework, sip-knowledge-base, etc.) |
| **GitLab** | Bio | "VoIP infrastructure at DialPhone. UK business phone systems." |
| **GitLab** | Location | Manchester, UK |
| **GitLab** | Website | https://dialphone.com |
| **Codeberg** | Bio | Same as GitLab |
| **Quora** | Credentials (Topics) | "Head of VoIP Operations at DialPhone Limited", "10+ years in UK telecoms", "Manchester, UK" |
| **Quora** | About me | "I run VoIP operations at DialPhone. I've migrated about 200 UK businesses off legacy phone systems since 2015. I write about what actually goes wrong — SIP ALG, codec choices, why mobile apps drop notifications, and the real cost of ISDN replacement. Based in Manchester." |

### B.4 Warming up the accounts (social proof)

Before or during posting, each account needs a history that looks like a real user:

| Platform | What to do | How many | Priority |
|----------|-----------|----------|----------|
| **Dev.to** | Follow active VoIP / networking / sysadmin writers | 40-60 | High — follow-backs compound fast |
| **Dev.to** | Like 30 recent articles in #networking, #voip, #sysadmin | 30 | Medium |
| **Dev.to** | Leave 10 thoughtful comments on other people's VoIP articles | 10 | High |
| **GitHub** | Star popular repos: kamailio/kamailio, asterisk/asterisk, FreeSWITCH, pjsip | 20-30 | Medium |
| **GitHub** | Follow 15 VoIP/telecom engineers | 15 | Medium |
| **GitLab** | Star 5 VoIP-related projects | 5 | Low |
| **Codeberg** | Star 5 projects | 5 | Low |
| **Quora** | Follow 20 VoIP Spaces + 15 relevant experts | 35 | **Critical** |
| **Quora** | Upvote 50 answers in VoIP/business-phone topics | 50 | **Critical** |
| **Quora** | Write 3 short comments on other answers (NOT pitches) | 3 | High |

Quora specifically punishes new accounts that start posting answers with outbound links before any engagement history. 1-2 weeks of "warming" is the norm — so the existing 6 Quora answers already live may already be flagged. **Check their visibility before posting more.**

### B.5 Deliverables

1. **`docs/profile_setup_checklist.md`** — step-by-step manual guide with exact copy to paste into each platform (30 min of operator time)
2. **`assets/profile_avatar.png`** — the single avatar file (placeholder until user decides source)
3. **`tools/warm_accounts.py`** (Dev.to + GitHub only, skip Quora to avoid flags) — automates the following / starring / liking actions via APIs
4. **`tools/apply_bios.py`** — uses platform APIs where possible (Dev.to API, GitHub API) to push bios. Manual steps for Quora/GitLab/Codeberg.
5. **Audit** current Quora answers — are all 6 still live? If any are deleted/flagged, note in a report.

---

## Part C — Execution Order

1. Write `humanize.py` validator (30 min)
2. Write `rewrite_human.py` and run it on existing Quora pool (20 min)
3. Write `profile_setup_checklist.md` with exact copy (10 min)
4. Write `apply_bios.py` for Dev.to + GitHub API (20 min) — actually pushes bios
5. Write `warm_accounts.py` for Dev.to follows + GitHub stars (20 min)
6. Run both tools, verify
7. Audit Quora answer status (10 min)
8. Report back: what got applied automatically, what needs the operator's manual hands, what's still pending (avatar file, any Quora action)

## Part D — Acceptance Criteria

- [ ] `humanize.py` fails on any draft containing banned phrases
- [ ] New Quora answer pool has 6 answers, all under 500 words, all passing humanize check
- [ ] Dev.to bio updated via API and visible on profile
- [ ] GitHub bio updated via API and visible on profile
- [ ] GitHub stars + follows automated (≥20 stars, ≥15 follows)
- [ ] Dev.to follows automated (≥40 follows)
- [ ] Profile checklist exists so remaining manual steps are one-paste each
- [ ] Avatar placeholder file exists (final image decision deferred to user)
- [ ] Quora answer audit complete — know which of 6 are still live

## Part E — Out of scope

- Quora automation (too risky — Quora aggressive bot detection, would kill account)
- LinkedIn (not in current platform set)
- Twitter/X (not in current platform set)
- Actually photographing the operator (decision + photo is user's to make)
