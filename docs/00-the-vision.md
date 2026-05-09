# 00 — The Vision

> Why I built a council instead of buying a Manus subscription.

## The problem with one big agent

Manus.ai, Devin, ChatGPT-with-tools — they're all the same shape. **One model.** Big. Smart. Trained on a lot of work. You give it a hard question, it produces an answer. You don't see *why*; you see *what*.

That's fine when you trust the model. It's a problem when:

- You're the kind of thinker who needs to **see the disagreement** before you trust the conclusion.
- You want to **catch the answer that one perspective missed.**
- You can't afford to burn $20+/day on inference for a hobby project.
- You need an **audit trail** — what did each lens say, before the synthesis?
- You're a polymath whose thinking lives in *contradictions* — Stoic AND Kantian AND empiricist AND first-principles, all true at once — and a single model collapses contradictions instead of holding them.

The council fixes all of that.

## What "divide and conquer" actually means here

A typical big-model approach:

```
question → [BIG MODEL] → answer
```

The council:

```
question → Tenet (chair, route)
              │
              ├──▶ Ana    (Kantian — what's the duty here?)
              ├──▶ Civic  (Mill — what produces the most good?)
              ├──▶ Hannah (Douglas/Tversky — what category-error
              │             is hidden in the framing?)
              ├──▶ Bob    (Freud — what's the room not saying?)
              ├──▶ Pip    (Vignelli — does the form serve the function?)
              ├──▶ noN    (Jung — what's the shadow nobody sees?)
              │
              ▼
         Tenet synthesises (Musk first-principles + Fuller systems)
              │
              ▼
         Otto executes the resulting action
              │
              ▼
         Radar scribes the deliberation
```

Each lens is **a small model with a sharp specialty**. None of them needs to be GPT-5. A 7B-parameter Llama with a tight Kantian SOUL prompt is a better Kantian than GPT-4o without the prompt — because the prompt does the work the parameters would otherwise need to.

This is the real insight: **specialisation via prompt is cheaper than capability via parameters.**

## Why this beats a Manus-class agent (for thinking work)

**1. The room catches what one perspective misses.**
If you ask a single GPT-4o "should I take this contract?" it'll synthesise a sensible answer. Ask a council and Civic will tell you it produces good consequences, Ana will tell you it violates a duty, Hannah will tell you the "contract" framing hides a category error, and noN will say something nobody wanted to hear. *That's* deliberation. Single models can simulate it but rarely commit to it.

**2. You can read the deliberation log.**
Every council message is timestamped and lens-tagged. When you don't like a decision, you can trace which lens convinced Tenet. You can re-prompt the lens that got it wrong. With Manus, the synthesis is opaque.

**3. You can swap a brain without rebuilding the system.**
Tenet on `qwen3-max` today. Tomorrow he might be on `claude-sonnet-4.5` or `kimi-k2` — same SOUL, same lens, different brain. The council is **architecture-first, model-second.**

**4. It runs on a Mac, on $0 of free-tier capacity.**
Manus's whole pitch is *we run a GPU cluster so you don't have to.* But you don't *need* a cluster — you need 9 small models, free-tier-priced, distributed across 4-5 providers so no single rate limit kills the room. See [`05-providers-zero-cost.md`](05-providers-zero-cost.md).

## What this is NOT

- **Not a Manus replacement for one-shot tasks.** If you want "build me a SaaS in 4 hours," go pay Manus. The council is for *thinking* work.
- **Not a multi-agent framework.** This isn't AutoGen or CrewAI. Those are programming abstractions; this is a *room* you join in Telegram, with personalities you read and learn from.
- **Not autonomous.** The council deliberates; you decide. Otto executes only after Tenet pins a decision and you don't object.

## The cost philosophy

> **The $0 doctrine:** if a thing can be done at $0, do it at $0 — even if "$5/month" is technically affordable. The discipline of refusing to pay forces better architecture.

In practice:
- Free-tier providers cover the *vast majority* of council load.
- Paid providers cover the chair (Tenet) + 1-2 reliability-critical bots.
- Local fallback (phi4-mini via Ollama) covers the doomsday-scenario.
- Skills (podcast generation, image generation, etc.) pay-per-use, the costs are pennies.

The total monthly bill: **~$15-25 for a daily-use council.** Strict-zero variant possible at the cost of slightly weaker chair reasoning.

→ Next: [`01-architecture.md`](01-architecture.md) for the full bot list and how they fit together.
