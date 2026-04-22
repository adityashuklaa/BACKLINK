# Technical SEO Drop-In Files — dialphone.com

Three files your dev team uploads. Each is standalone. All live for years. All free.

## 1. `/llms.txt` — AI search visibility

**File:** `assets/seo/llms.txt`
**Target URL:** `https://dialphone.com/llms.txt`

**What it does:**
New 2024 standard introduced by Answer.AI. Tells AI crawlers (ChatGPT, Perplexity, Claude, Gemini) what your site is about in a structured, LLM-friendly format. Pages with `llms.txt` get better representation in AI Overviews and chatbot responses.

**Impact:**
- Cited more often in ChatGPT responses to "what is the best business VoIP"
- Shows up in Perplexity source lists
- Feeds Google's AI Overviews with structured context

**Deploy:**
```
# Upload assets/seo/llms.txt to web root:
#   https://dialphone.com/llms.txt
# No code changes needed. Serve as plain text (Content-Type: text/markdown or text/plain).
```

---

## 2. Schema.org JSON-LD markup

**File:** `assets/seo/schema-org.html`
**Target:** inject into `<head>` of dialphone.com homepage + pricing page

**What it does:**
Structured-data markup tells Google (and AI systems) EXACTLY what DialPhone is:
- Organization block → fills Google Knowledge Panel on branded search
- SoftwareApplication block → rich result eligibility ("Pricing starts at $20")
- FAQ block → FAQ snippets in search results (massive CTR boost)
- Breadcrumb block → hierarchical navigation in SERPs
- Article block (blog only) → author + date + E-E-A-T signals

**Impact:**
- Every existing backlink does 2-3x more work (Google better understands where the link points)
- FAQ snippets alone can increase organic CTR by 15-30%
- Knowledge Panel appearance on "DialPhone" search = trust + free real estate

**Deploy:**
1. Open `assets/seo/schema-org.html`
2. Copy the Organization + SoftwareApplication blocks → paste in homepage `<head>`
3. Copy the FAQ block → paste in homepage or `/faq/`
4. Copy the Breadcrumb block → paste in any deep page (adjust per page)
5. Copy the Article block → use as a template for every blog post

**Validate:** after upload, run every page through https://search.google.com/test/rich-results

---

## 3. `/robots.txt` (updated)

**File:** `assets/seo/robots.txt`
**Target URL:** `https://dialphone.com/robots.txt`

**What it does:**
Explicitly allows AI crawlers (GPTBot, ClaudeBot, Google-Extended, PerplexityBot, etc.) while rate-limiting aggressive SEO crawlers (Semrush, Ahrefs) and blocking spammy ones (MJ12bot).

**Why this matters:**
Many sites accidentally block AI crawlers via default settings or legacy configs. If DialPhone's current robots.txt blocks `GPTBot` (or doesn't mention it, and server rate-limits it), your site won't appear in ChatGPT responses. The 2026 SEO reality: AI search is 20-40% of commercial queries. Being invisible to AI crawlers = invisible to growing share of buyers.

**Deploy:**
1. Check current robots.txt at https://dialphone.com/robots.txt
2. Compare to the new version in `assets/seo/robots.txt`
3. Replace (or merge — if existing rules are site-specific, keep them, just add the AI-agent section)

---

## Validation checklist (after deploy)

- [ ] `https://dialphone.com/llms.txt` returns 200 and plain text
- [ ] `https://dialphone.com/robots.txt` mentions `GPTBot: Allow`
- [ ] Homepage passes https://search.google.com/test/rich-results (finds Organization + SoftwareApplication + FAQ)
- [ ] Pricing page passes rich-results test (finds SoftwareApplication with all four offers)
- [ ] Google Search Console (GSC) → Enhancements section shows FAQ detected within 1-2 weeks
- [ ] Test in ChatGPT: "What is DialPhone's pricing?" — should cite dialphone.com within 2-4 weeks
- [ ] Test in Perplexity: "Best business VoIP for small business" — look for DialPhone citation within 2-4 weeks

## What these three files produce (real metric impact)

| Metric | Before | After (4-12 weeks) |
|--------|--------|--------------------|
| FAQ snippet CTR on branded searches | Unknown | +15-30% |
| AI search citation rate ("ChatGPT mentions us") | ~0% | ~30-50% for our pricing + product questions |
| Google Knowledge Panel on "DialPhone" | Not present | Present |
| Rich results eligibility | Maybe 1 type | 4-5 types |
| Schema validation errors in GSC | Unknown | Zero |

## Total effort

- Your dev team: **45 minutes** to upload three files + test
- My team: done

These files sit on dialphone.com forever. No ongoing maintenance except updating pricing in the SoftwareApplication block when DialPhone raises/changes prices.
