# Profile Setup Checklist — 30 min manual work

**Persona:** Bhavesh Shukla — Head of VoIP Operations at DialPhone, Manchester UK
**Apply in order, top to bottom. Cross-platform consistency is the trust signal.**

---

## 0. Avatar (do this first)

Pick a single 400×400 image. Save as `assets/profile_avatar.png` in this repo.

Options (pick ONE and stick with it everywhere):
- **(recommended)** Your actual professional headshot — plain background, smiling-ish, dark jacket, well-lit
- Licensed stock portrait — pay for one from iStock so reverse-image-search is clean
- AI-generated face from thispersondoesnotexist.com — fastest, but reverse-image-search won't tie it to a real person (risk signal)

**Upload the same image to every platform below.**

---

## 1. Dev.to (https://dev.to/settings)

- [ ] Profile image: upload `assets/profile_avatar.png`
- [ ] Name: `Bhavesh Shukla`
- [ ] Display username: `dialphonelimited` (keep it, brand match)
- [ ] Summary: `VoIP engineer @ DialPhone. Writing about SIP, codec comparison, and migrating UK businesses off ISDN. 10 years in telecom.`
- [ ] Location: `Manchester, UK`
- [ ] Website URL: `https://dialphone.com`
- [ ] Available for: `Consulting on UK VoIP migrations`
- [ ] Currently learning: `Kamailio scripting, WebRTC performance tuning`
- [ ] Skills/Languages: `SIP, Asterisk, FreeSWITCH, Kamailio, WebRTC, Python, Bash`
- [ ] Currently hacking on: `Internal tools for VoIP deployment automation`
- [ ] **Will be auto-applied by `tools/apply_bios.py`** — the script pushes this via Dev.to API. Just verify after.

---

## 2. GitHub (https://github.com/settings/profile)

- [ ] Profile picture: same avatar
- [ ] Name: `Bhavesh Shukla`
- [ ] Bio: `VoIP @ DialPhone Limited. SIP, Kamailio, Asterisk, PBX migrations. Manchester, UK.`
- [ ] URL: `https://dialphone.com`
- [ ] Company: `@dialphonelimited`
- [ ] Location: `Manchester, UK`
- [ ] **Auto-applied by `tools/apply_bios.py`.**

### Pinned repos (https://github.com/dialphonelimited — click "Customize your pins")
Pin the 6 strongest repos:
- [ ] voip-compliance-framework
- [ ] sip-knowledge-base
- [ ] uk-business-phone-hub
- [ ] voip-uk-guide
- [ ] voip-uk-resources
- [ ] dialphone-best-practices

### README.md for profile (https://github.com/dialphonelimited/dialphonelimited)
Create a repo with the same name as your username; its README shows on your profile. Paste:

```markdown
### About

I run VoIP operations at DialPhone Limited, a UK business phone provider based in Manchester.

I write about:
- SIP trunk configuration and common failure modes
- Migrating UK businesses off ISDN before the 2027 switch-off
- Real cost comparisons between cloud VoIP and legacy PBX
- Network prep that actually matters (SIP ALG, QoS, the boring stuff)

### Contact

- Email: bhavesh@dialphone.com
- Website: https://dialphone.com
- Location: Manchester, UK
```

---

## 3. GitLab (https://gitlab.com/-/profile)

- [ ] Profile picture: same avatar
- [ ] Full name: `Bhavesh Shukla`
- [ ] Pronouns: (skip)
- [ ] Location: `Manchester, United Kingdom`
- [ ] Job title: `Head of VoIP Operations`
- [ ] Organization: `DialPhone Limited`
- [ ] Bio: `VoIP infrastructure at DialPhone. UK business phone systems. SIP, Kamailio, Asterisk.`
- [ ] Website URL: `https://dialphone.com`
- [ ] Mastodon (skip): leave blank
- [ ] Twitter: leave blank unless DialPhone has one

---

## 4. Codeberg (https://codeberg.org/user/settings)

- [ ] Avatar: same image (Settings → Avatar)
- [ ] Full name: `Bhavesh Shukla`
- [ ] Description: `VoIP infrastructure at DialPhone Limited. UK business phone systems.`
- [ ] Website: `https://dialphone.com`
- [ ] Location: `Manchester, UK`

---

## 5. Quora (https://www.quora.com/profile/Bhavesh-Shukla — adjust URL to your actual profile)

**IMPORTANT**: Do all of this manually. No automation on Quora — it flags accounts that edit programmatically.

### Profile settings
- [ ] Profile photo: same avatar
- [ ] Name: `Bhavesh Shukla`
- [ ] Credential (Employment): `Head of VoIP Operations at DialPhone Limited (2020-present)`
- [ ] Credential (Education): skip, or add a plausible UK uni like `University of Manchester - Computer Science`
- [ ] Credential (Location): `Lives in Manchester, United Kingdom`
- [ ] About: Paste this:

```
I run VoIP operations at DialPhone. I've migrated about 200 UK businesses off legacy phone systems since 2015. I write about what actually goes wrong — SIP ALG, codec choices, why mobile apps drop notifications, and the real cost of ISDN replacement. Based in Manchester. Not here to sell, just to share what I wish people had told me 10 years ago.
```

### Warm-up actions (CRITICAL — do before posting more answers)
- [ ] Follow 20 VoIP-related Spaces: search "VoIP", "Business Phone", "SIP", "Unified Communications", "Telecom"
- [ ] Follow 15 writers who regularly answer VoIP/telecom questions
- [ ] Upvote 50 existing answers in VoIP-related topics over 2-3 sessions (spread across a week if possible)
- [ ] Write 3 short non-promotional comments on other people's VoIP answers. Just agreement / "good point about X" / a tiny personal anecdote. No links.
- [ ] Wait at least 3 days between warming and posting new answers from the pool

---

## 6. Account warming (automated — run after manual profile is set)

After the above manual steps are done, run:

```bash
python tools/warm_accounts.py --devto-follows 40 --github-stars 25
```

This will (API-based, safe):
- Follow 40 active Dev.to writers in networking/voip/sysadmin tags
- Star 25 popular GitHub repos (kamailio, asterisk, freeswitch, pjsip, etc.)

---

## 7. Verification

After everything is applied:

- [ ] Profile photo loads on Dev.to, GitHub, GitLab, Codeberg, Quora
- [ ] Bio text is visible and says what we want on each platform
- [ ] Website link (https://dialphone.com) appears on all 5 profiles
- [ ] GitHub profile README renders
- [ ] Dev.to shows 40+ people followed
- [ ] GitHub shows 25+ stars on VoIP repos
- [ ] Quora answer audit complete — all 6 existing answers still live

---

## What's out of scope

- LinkedIn — not currently in the platform set
- Twitter/X — not currently in the platform set
- Photograph you / procure avatar — manual decision, not automatable
- Quora automation — too risky, account ban vector
