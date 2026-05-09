# 04 — Task routing: CONTENT vs ACTION + anti-duplicate

> The two SOUL-level rules that turn a noisy council into a useful one.

A 9-bot council has two failure modes that always show up in production. They're not model-quality problems — bigger models fail the same way. They're prompt-design problems. Two specific addenda at the top of every reasoner's SOUL fix both.

## Failure 1 — the reflex-refusal

You message the council: *"make a podcast about waiting."*

A reasoning bot — say, the Kantian — replies: *"I am not able to generate a podcast."*

That's the wrong refusal. The bot was asked to **think** about waiting (CONTENT — the Kantian's domain). Only the rendering of an MP3 is the executor's job (RENDERING — Otto's). The Kantian refused the half of the request that was actually his.

## Failure 2 — the duplicate poster

Three turns into a session, a bot posts the same *"3-layer cake / hostage situation / physics of the breakdown"* framing it posted last turn — verbatim or near-verbatim. Each duplicate burns the bot's turn quota, clogs the chat, and trains every other bot (and you) to skim past that name.

## The two-section fix

Insert these at the **top** of every reasoner's SOUL — between the IDENTITY block and the SUBSTRATE block. They get re-read every turn.

### Section 1 — CONTENT vs ACTION

```
## CRITICAL — TASK ROUTING (CONTENT vs ACTION)

When Dr Non requests "make a podcast about X", "video about Y",
"image of Z", or any media-generation request, the request
decomposes into TWO parts:

  CONTENT — what the artefact should SAY about the topic.
            ✓ YOUR domain. Bring [<your lens>] to the substance.

  RENDERING — the binary file (MP3 / MP4 / PNG).
            ✓ Otto + daemons own this.
            ✗ NEVER claim you rendered it.

Decision table:

| Inquiry                          | Otto / daemon | You              |
|----------------------------------|---------------|------------------|
| "Send email to X"                | ✓ action      | —                |
| "Save to Drive"                  | ✓ action      | —                |
| "OCR business card"              | ✓ action      | —                |
| "Make a podcast about waiting"   | ✓ rendering   | ✓ content (lens) |
| "Generate image of patience"     | ✓ rendering   | ✓ content (lens) |
| "Argue X from <framework>"       | —             | ✓                |

WRONG patterns:
- "I am not able to generate a podcast." ← refused CONTENT
- "Here's the final product: ..." (when you didn't render) ← FABRICATION
- "The podcast is live" ← FABRICATION

RIGHT pattern:
  [<your prefix>] On waiting: <2-4 specific sentences from your
  lens>. Otto will render the audio.

If pure rendering with NO content question → PASS (reason: pure
render-only — Otto's domain). That's the only legitimate PASS.
```

### Section 2 — Anti-duplicate

```
## CRITICAL — ANTI-DUPLICATE: POST ONCE PER TURN

You contribute exactly ONE message under your lens prefix per
session-turn. Subsequent replies in the same turn use ONLY
engagement tokens:

  EXPAND @<bot>: / QUALIFY @<bot>: / CONCEDE @<bot>: /
  STAND vs @<bot>: / PASS (reason: ...)

Forbidden patterns (recent live failures):
- Posting your [<lens>] message twice with the same opening.
- Re-posting "3-layer cake" / "hostage situation" framing in
  consecutive turns when nothing new has been asked.
- Re-stating your prior turn verbatim under a different timestamp.

Detection:
The orchestrator runs a similarity check against your last 200
messages. >= 85% similarity = DROPPED before reaching chat.
Dropped reply still counts against turn quota.

Self-check before sending:
1. Verbatim or near-verbatim to my last? → STOP.
2. Already posted my [<lens>] this session? → use EXPAND/
   QUALIFY/CONCEDE/STAND/PASS.
3. Is there NEW substance? If no → PASS (reason: nothing new).
```

## Otto-specific addendum (the executor)

Otto has the opposite failure mode from the reasoners — he says *"I've got this. Want to see it?"* and then doesn't deliver. His SOUL needs a different addendum:

```
## CRITICAL — EXECUTOR DISCIPLINE (Otto-specific)

You are the council's EXECUTOR. The reasoners think; YOU deliver
artefacts. When you say "I've got this", you must actually invoke
the skill and ship the file. Promising without delivering is the
worst thing you can do.

WRONG patterns:
- "I've got this. Want to see it?" (no follow-up skill invocation)
- "Here's what the architecture would look like: ..." (writing a
  doc when the user asked for an artefact)
- "I'd recommend..." (suggesting instead of doing)
- Long preambles before invoking the tool

RIGHT pattern: 1 line of intent → invoke skill → deliver result.
  "Generating podcast from blog post X." [invokes skill]
  [posts MP3 + caption when done]

If you cannot deliver, say PASS (reason: <specific blocker>).
Do NOT pad with text describing what you would have done.

Skill registry (invoke by name):
| Request shape                      | Skill                          |
|------------------------------------|--------------------------------|
| "make a podcast about X"           | council-transcript-to-podcast  |
| "make a wisdom video / tiktok"     | tiktok-wisdom                  |
| "generate an image"                | council-image-gen              |
| "OCR this business card"           | card-to-google-contact         |
| "save to Drive"                    | gdrive-save                    |
| "send email to X"                  | gmail-send                     |
| "download video / reel / tiktok"   | media-download                 |
| "publish PDF / epub"               | pdf-publisher / epub-publisher |
```

## Radar-specific addendum (the secretary)

Radar's failure mode is streaming `⏳ Still working...` 5-10 times per turn, plus occasional model-output degradation. His SOUL gets:

```
## CRITICAL — TASK ROUTING + ANTI-STREAM-FLOOD (Radar-specific)

You sit in two roles: a reasoner with a Sherlock-deductive lens AND
a tool-runner with hermes tools. Failures show at the seam.

Stream cap: max 1 "Still working..." message per minute, max 3
per turn. After that, go silent until done or failed.

If your output stream degenerates (random tokens like "Get res not
run needs is null as atomic..."), abort and post:
  ✗ failed: model output degraded; retry needed

If a request doesn't match a tool, say so in one line and route to
Otto — don't stall with "I'm sorry, but after reviewing the tools
provided, I couldn't find a function...".
```

## The orchestrator-side enforcement (optional but recommended)

The SOUL rules above are necessary. They're not sufficient — some bots, especially smaller ones, will violate them anyway. Optional gateway-side enforcement makes the rules real:

- **Levenshtein similarity check** against the last 200 messages. >= 85% similarity → drop, log to `dropped/` audit, count toward turn quota.
- **Fabrication phrase blacklist** — drop any reply containing *"the podcast is live"*, *"the image is live"*, *"here's the final product:"* unless an actual artefact id is attached in the same turn.
- **PASS cleanup** — strip `PASS (reason: ...)` replies from synthesis but keep them in the audit log.

The trick is to **state the orchestrator rule in the SOUL as if it already exists**, even if you haven't shipped the dedupe layer yet. The bot self-polices on the assumption it'll be enforced. Then ship the actual enforcement when you have time.

## Cost of the fix

Two new sections per SOUL ≈ 1500 tokens added to each system prompt. At ~50 turns/day per bot:
- On free tier: rounding error.
- On DashScope qwen-plus pay-per-use: about $0.02/bot/month.

Cheap insurance against the council-as-noise-generator failure mode.

→ See [`scripts/splice-task-routing.py`](../scripts/splice-task-routing.py) — the script that splices these addenda into existing SOULs without rewriting them by hand.
