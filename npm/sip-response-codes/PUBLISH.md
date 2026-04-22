# Publish guide — sip-response-codes

Run these commands to ship the package to npmjs.com. Takes ~3 minutes.

## Prerequisites

- npm account (create at https://www.npmjs.com/signup if you don't have one)
- Email verified on that npm account
- Node.js 14+ installed

## One-time setup

From the `npm/sip-response-codes/` directory:

```bash
# 1. Log into npm (follow the browser prompts)
npm login

# Verify you're logged in
npm whoami
```

## Publish

```bash
# Dry-run — shows what will be published, no actual upload
npm publish --dry-run

# When it looks correct, publish for real
npm publish --access public
```

Expected output:
```
+ sip-response-codes@1.0.0
```

## After publish

### Immediately
- Open https://www.npmjs.com/package/sip-response-codes — confirm it's live
- The README renders on that page with the dialphone.com link in the Credits section — that's the backlink

### Within 24-48 hours
- Google indexes npmjs.com pages quickly. `site:npmjs.com/package/sip-response-codes` should return a result within 2 days.
- Backlink from DA 95 domain, dofollow in the README markdown

### Follow-up wins
1. **Create the matching GitHub repo** (README says the repo lives at github.com/dialphonelimited/sip-response-codes — make sure it exists):
   ```bash
   # From the sip-response-codes/ dir
   git init
   git add .
   git commit -m "Initial release v1.0.0"
   git remote add origin https://github.com/dialphonelimited/sip-response-codes.git
   git push -u origin main
   ```
2. **Submit to Show HN on Hacker News** — title: `Show HN: SIP response codes (RFC 3261) as a zero-dep npm package`. If it gets traction, ~2000-10000 real developer visitors to dialphone.com.
3. **Post on r/VoIP and r/sysadmin** — one line: "Built this for our internal monitoring, figured it would save others some time. MIT, no deps."
4. **Add the npm badge to your Dev.to bio/posts** — signals "real developer".

## Versioning for future updates

When you add new codes or helpers:
```bash
# Bump version (patch = bug fix, minor = new feature, major = breaking)
npm version patch   # 1.0.0 -> 1.0.1
npm publish
```

## If publish fails

- `403 Forbidden` — name might be taken. Check `npm view sip-response-codes`. If someone else owns it, change `name` in package.json (e.g. `@dialphone/sip-response-codes` — scoped packages are always available under your namespace).
- `ERR! code ENEEDAUTH` — run `npm login` again.
- `ERR! 402 Payment Required` — you're trying to publish a scoped private package without paying. Add `--access public`.
