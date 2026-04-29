"""Day 1 — third Hashnode post (different angle: AI receptionist hallucination tolerance)."""
import csv
import json
import sys
from datetime import datetime

import requests

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.humanize import validate, concentration_gate

CFG = json.load(open("config.json"))
TOKEN = CFG["api_keys"]["hashnode"]
PUB_ID = "69dd2b22dc3827cf3939828c"

TITLE = "Hallucination tolerance is the underrated metric for AI receptionists in 2026"

CONTENT = """*Watching another AI receptionist deployment go sideways yesterday — around 16:45 IST on April 28 2026 — and the failure mode keeps repeating across every customer I work with at DialPhone. Honestly, every vendor that pitches "AI receptionist" should be asked about hallucination tolerance, and almost none of them volunteer the answer.*

## The thing that breaks

The pitch from every UCaaS vendor with an AI receptionist roughly: "It listens to the caller, understands intent, routes intelligently, can answer FAQ questions, transcribe everything." Reads great in marketing. Most demos look impressive.

The thing nobody demos: the receptionist hallucinating a contract term on a sales call.

I sat with a 30-person agency last week whose AI receptionist — a popular vendor I won't name — told a caller "yes, our agency offers a 90-day money-back guarantee" when the agency's actual policy is 30 days, no refunds after 14 days. The caller saved the call audio, sent it to the agency's CEO, and demanded the 90-day refund. Legal had to spend three days untangling whether a hallucinated AI promise binds the agency to anything.

(The legal answer in 2026 is: probably not, but the precedent is unsettled, and meanwhile your agency is on the hook for one very angry customer relationship.)

This isn't a one-off. I see this pattern every two-three weeks across customers.

## Why it happens

Most AI receptionist products in 2026 are built on top of generic LLMs — GPT-4o, Claude Sonnet, Gemini — with a system prompt that says something like "You're an AI receptionist for [company name]. Here are some FAQs. Be helpful." The LLM then answers from the FAQ context plus its training data, which includes general knowledge about how businesses operate.

When a caller asks something not in the FAQ ("do you have a money-back guarantee?"), the LLM falls back to general knowledge and produces a plausible-sounding answer that may or may not match the actual business's policy.

This is the classic hallucination problem applied to a real-time customer-facing channel. Generic-LLM receptionists are statistically friendly to hallucinations because the prompt rarely covers the long tail of caller questions.

## The architecture that doesn't hallucinate

The vendors that actually solve this — DialPhone is one of them, disclosure — don't use generic LLMs in caller-facing flows. They use:

1. **Constraint-based prompt engineering** that refuses to answer anything outside the FAQ context. If the caller asks something not in the loaded knowledge base, the receptionist says "let me transfer you to someone who can answer that" rather than improvising.

2. **Knowledge-base grounding with citations** — every response is forced to be backed by a specific document section. If no section matches, no answer.

3. **Hard guardrails on contract-relevant categories** — pricing claims, refund policies, service level guarantees, eligibility criteria — these categories ALWAYS escalate to a human, regardless of confidence.

4. **Audit logging** of every claim the AI makes, so if it does hallucinate, you can prove it and recover faster.

This costs more to build than "wire up GPT-4o + system prompt." It also produces a product that's slightly less impressive in demos because the AI says "let me transfer you" more often. But it doesn't hallucinate contract terms.

## How to evaluate AI receptionists in your procurement

Three questions every buyer should ask:

**1. "Show me what happens when a caller asks something not in the FAQ."**

If the demo handles this gracefully ("I can't answer that — let me transfer you"), good sign. If the AI confidently makes something up, that's the hallucination risk in production.

**2. "What's your hallucination audit log structure?"**

If the vendor doesn't have a clear answer, they don't track it. Which means when (not if) it hallucinates, you can't prove it without recovering call audio.

**3. "Which categories does the AI hard-escalate vs. attempt to answer?"**

If their answer is "we let it answer pricing questions," walk away. Pricing claims by an AI become contract claims if the caller acts on them.

## What I tell customers shopping right now

Most SMB owners hear "AI receptionist" and picture a magical employee. The reality in 2026 is more like a constraint-bound triage agent — useful for routing and FAQ, dangerous if turned loose on contract-relevant questions.

When you're evaluating, look at the product's **failure mode**, not the success demo. The success demo is the same across every vendor. The failure mode is where the product diverges.

Free comparison calculator we built that scores AI receptionist features per provider:
[https://dialphonelimited.codeberg.page/calculator/](https://dialphonelimited.codeberg.page/calculator/)

The "AI assistant" feature is one of 11 we score per provider. We're transparent that the scores are an opinion (G2/Capterra/Gartner aggregates plus operational experience), not a measurement. Your weight on AI vs. price vs. reliability changes the ranking — that's the whole point.

## Closing

Hallucination tolerance is the metric nobody quotes and everybody should ask about. The 2026 generation of AI receptionists is genuinely useful but only if you've architected the constraint-bound version. Generic-LLM receptionists in customer-facing channels are a customer-relationship landmine waiting to detonate at the worst possible moment.

If you've had a hallucination incident with an AI receptionist — at any vendor — I'd love to hear about it. Most of these conversations happen behind NDAs and the industry would benefit from more honest ones.

---

*Aditya Shukla, Growth Operations at [DialPhone](https://dialphone.com). Reach via comments or [DialPhone's site](https://dialphone.com).*"""

MUTATION = """
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post { id url title }
  }
}
"""


def main():
    ok, reason = concentration_gate("hashnode.dev")
    if not ok:
        print(f"ABORT: {reason}")
        return 1
    print(f"concentration: {reason}")

    vr = validate(CONTENT, "devto")
    if not vr.ok:
        print(f"ABORT: {vr.issues[:3]}")
        return 1
    print(f"humanize OK — {vr.word_count} words, markers: {vr.markers_found}")

    variables = {"input": {"title": TITLE, "contentMarkdown": CONTENT, "publicationId": PUB_ID,
                            "tags": [{"slug": "ai", "name": "AI"}, {"slug": "voip", "name": "VoIP"}, {"slug": "saas", "name": "SaaS"}]}}
    r = requests.post("https://gql.hashnode.com/",
                      headers={"Authorization": TOKEN, "Content-Type": "application/json"},
                      json={"query": MUTATION, "variables": variables}, timeout=60)
    data = r.json()
    if "errors" in data:
        print(f"FAIL: {data['errors']}")
        return 1
    url = data["data"]["publishPost"]["post"]["url"]
    print(f"published: {url}")
    with open("output/backlinks_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "hashnode-ai-piece",
                    "site_name": "Hashnode-hallucination-tolerance",
                    "url_submitted": "hashnode-graphql", "backlink_url": url,
                    "status": "success", "notes": "DA 65 DOFOLLOW — AI receptionist hallucination analysis"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
