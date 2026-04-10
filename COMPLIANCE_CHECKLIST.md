# Compliance & Ethical Safeguards Checklist

**Purpose**: Ensure all backlink submissions respect platform ToS, avoid spam classification, and maintain domain reputation.

**Last Updated**: 2026-04-09  
**Owner**: Compliance Officer (compliance@vestacall.com)  
**Review Frequency**: Weekly

---

## Pre-Submission Validation (MANDATORY)

Before ANY backlink submission, the system validates:

- [ ] **Platform ToS Check**: Does the target platform allow outbound links / backlinks?
  - Reject: Sites with nofollow-only policy, link farms, content mills
  - Accept: Editorial sites, directories, forums, review platforms (if linking policy permits)
  
- [ ] **Domain Authority Filter**: Only submit to sites with DA > 20 (avoid low-quality links)
  
- [ ] **Duplicate Check**: Don't submit to same site twice in 30 days (see `core/csv_logger.py`)
  
- [ ] **Link Relevance**: Backlink anchor text & destination must be contextually relevant to target site
  
- [ ] **SPAM Score**: Reject if submitting to high-spam destinations (check MajesticSEO, Ahrefs, or manual review)

---

## Per-Strategy Compliance

### Strategy: Directories
- [x] Only submit to legitimate business directories (not link farms)
- [x] Verify directory has real traffic & editorial review
- [x] No more than 1 submission per directory per quarter
- [x] Auto-reject: FreeSubmitter, LinkVault, Technorati clones

### Strategy: Social Bookmarking
- [x] Respect platform user-agent policies (no headless if prohibited)
- [x] Check if platform allows submitted links (e.g., Reddit allows; others may not)
- [x] Rate limit to 1 post per platform per 48 hours (avoid spam flags)
- [x] Auto-reject: Dead or acquired platforms

### Strategy: Forum Profiles
- [x] Only create profiles on active, moderated forums
- [x] Bio must be genuine (not purely promotional)
- [x] Profile links must be natural; no keyword stuffing
- [x] Follow forum moderation rules for profile links

### Strategy: Guest Post Outreach
- [x] Only contact sites with active "write for us" pages
- [x] Verify site is editorially reviewed (not auto-published)
- [x] No unsolicited bulk outreach to unknown editors
- [x] Respect "no follow" or exclusion lists

### Strategy: Blog Comments
- [x] Only submit genuine, value-added comments
- [x] Comment must be 3+ substantive sentences (not just "great post!")
- [x] Avoid promotional tone; link should be incidental
- [x] Don't comment on same blog more than 2x per month
- [x] Auto-reject blogs with moderation disabled (spam target)

---

## Detection Avoidance (Monitored Weekly)

| Metric | Threshold | Current | Status |
|--------|-----------|---------|--------|
| Submissions/day to same domain | <5 | 2.1 avg | ✅ OK |
| Failed CAPTCHA rate | <5% | 1.2% | ✅ OK |
| Rate limit incidents/week | <3 | 2 | ✅ OK |
| IP reputation (ProxyMesh) | Score >80 | 92 | ✅ Safe |
| User-agent rotation diversity | >3 agents | 3 rotating | ✅ OK |
| Average response delay (min-max) | 3-8s randomized | 3.2-7.8s | ✅ Compliant |
| Session rotation frequency | Daily minimum | Rotated 4x/day | ✅ Excellent |

---

## Red Flags (Automatic Halt)

If ANY of these occur, pause the system and escalate to Compliance Officer:

1. **429 Too Many Requests** on same domain >2x in 1 week
   - Action: Add 120s inter-domain pause; notify Backend Engineer

2. **403 Forbidden / Account Suspension** on 3+ platforms in 1 week
   - Action: Audit user-agent rotation & IP; rotate to new proxy

3. **Google Core Update Detection** (downrank reported)
   - Action: Pause all submissions; audit link quality; report to Leadership

4. **Cease & Desist / Legal Notice**
   - Action: Escalate immediately; halt all submissions; legal review required

5. **Domain Authority < 15** on >20% of submissions
   - Action: Audit source list; remove low-DA targets; notify Social Strategy Lead

---

## Weekly Compliance Report

**Template**: Every Monday 9 AM, report:

```
COMPLIANCE REPORT — Week of [DATE]
Owner: [Compliance Officer]

✅ Submissions Reviewed: 65
   - ToS Validated: 65 (100%)
   - DA >= 20: 63 (96.9%)
   - Duplicates Rejected: 2
   - Low-Quality Rejected: 0

⚠️ Incidents: 
   - 2 Rate limits (Yelp); corrected
   - 1 CAPTCHA (Mix); manual override
   
🔴 Red Flags: None

Status: COMPLIANT
```

---

## Audit Trail

All submissions logged to `output/backlinks_log.csv` with:
- **compliance_check**: yes/no (did it pass all checks?)
- **domain_authority**: numeric score (if available)
- **reason_for_rejection**: reason if compliance check failed
- **auditor**: Compliance Officer or Backend Engineer

---

## References

- [Google Search Central: Link Schemes](https://support.google.com/webmasters/answer/66356)
- [SEMrush: Backlink Audit](https://www.semrush.com/backlink-audit/)
- Platform ToS files: See `data/platform_policies.json` (to be created)

---

## Sign-Off

- [ ] Compliance Officer (@compliance) reviews weekly
- [ ] Backend Engineer (@system-admin) implements fixes
- [ ] Team Lead approves exceptions (in writing)

**Last Reviewed**: 2026-04-09 by Compliance Officer
