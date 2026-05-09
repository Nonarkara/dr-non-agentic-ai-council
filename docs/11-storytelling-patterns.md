# 11 — Storytelling patterns (escaping the LLM cliché loop)

> Why every AI-drafted podcast script opens with *"I remember standing on the corner…"* — and how to stop that.

## The problem

Every modern LLM, given a prompt like *"write a 60-second wisdom video about waiting,"* will produce something that opens like this:

> *"I remember standing on a Bangkok street corner one humid afternoon, watching a vendor patiently roast satay over coals…"*

Or:

> *"I was sitting on the bus to Khon Kaen, watching the rice fields blur past my window…"*

Or:

> *"Picture this: it's 3am, you're staring at the ceiling, and you can't sleep…"*

Three different prompts, three near-identical openings. The reader catches it within a week and starts skimming. The voice that was supposed to be *yours* sounds like every other LLM-drafted piece on the internet.

This doc is the fix.

## Why it happens

Modern instruction-tuned LLMs are trained on a lot of "creative writing" data — Reddit r/WritingPrompts, fiction-writing how-tos, book-opening anthologies. The frequency-weighted advice in that training is **"open with a vivid scene the reader can picture."**

Then most prompt designers (myself included, in early iterations of this skill) accidentally reinforce the bias. My old `voice-preamble.md` literally said:

```
- NO theory-first opening. Drop the reader into a SPECIFIC concrete moment —
  a place, a person's name, a thing he did, a thing someone said.
```

That's *exactly* the instruction that produces "I remember standing on a corner." The model takes the rule literally and reaches for the most rehearsed shape it knows for "specific concrete moment."

## The fix — mine YOUR actual openings

**Step 1 — pull every opening you've ever written.** Run a script over your blog corpus / podcast transcripts / video scripts. Extract the first 1-2 sentences of each piece.

Example (Python, against a WordPress REST JSON dump):

```python
import json, re
posts = json.load(open("myblog.json"))
for p in posts:
    title = (p.get("title") or {}).get("rendered","")
    body  = (p.get("content") or {}).get("rendered","")
    body  = re.sub(r"<[^>]+>", " ", body)
    first = re.split(r"(?<=[.!?])\s+", body, maxsplit=1)[0]
    print(f"{title[:50]:50s} → {first[:120]}")
```

**Step 2 — group them into shapes.** Cluster by sentence-form, not by topic. You'll find 5-10 patterns repeating. Common ones:

- *"People ask me…"* + the question (direct-address opener)
- Confession of vulnerability (*"In my darkest hours…"*)
- You-just-saw-something (*"So, I'm scrolling X a couple days ago…"*)
- A quote landed back at the reader (*"'I am so glad to have met this version of you.' These 11 words…"*)
- Aphorism / declaration (*"Freedom is one of the most difficult topics."*)
- Buddhist / Taoist parable (*"A beautiful girl in the village was pregnant."*)
- Meta-acknowledgment (*"Hooray!"* / *"Let me savor the moment."*)
- Topic setup / classroom (*"As the title suggests…"*)

Your shapes will be different. The number (5? 8? 12?) is up to your range.

**Step 3 — write down what's NOT yours (the anti-patterns).** This is the critical part most people skip. Look at LLM-generated drafts of your work and list the openings that don't sound like you. Common ones:

- *"I remember standing in [place]…"*
- *"I was sitting on the bus when…"*
- *"It was a [season/weather] [time of day], and I…"*
- *"Picture this: [scene]…"*
- *"Imagine you are [doing thing]…"*
- *"In a world where [observation]…"*
- *"Have you ever [done thing] and thought…"*

**Step 4 — load both into the prompt.** When you draft, the system prompt should include:

1. The catalogue of YOUR shapes (with 2-3 example sentences per shape).
2. The list of anti-patterns the LLM defaults to.
3. A rotation rule: *"don't reuse the same shape in consecutive pieces."*

That third rule matters most. Without it, the model picks ONE of your shapes (usually the easiest one — the People-ask-me opener) and uses it every time. Rotation forces variety.

## How this skill implements it

The `tiktok-wisdom` skill ([implementation in agentic-ai-research/dr-non-diy-ai-council, PR #9](https://github.com/agentic-ai-research/dr-non-diy-ai-council/pull/9)) ships this pattern out of the box.

The relevant files in `examples/openclaw/skills/tiktok-wisdom/`:

```
prompts/
├── voice-preamble.md             ← base voice rules
├── openings-bible.md             ← 8 authentic Dr Non opening shapes,
│                                   with examples + anti-patterns
├── storytelling-techniques.md    ← 10 deeper structural moves
├── style-essay.md
├── style-listicle.md
└── strict-addendum.md

scripts/
└── build.py                      ← load_storytelling_reference()
                                    slices the bibles into the system
                                    prompt at draft time
```

The pattern: bibles live as plain Markdown. The script reads them and injects the rules into every prompt. When Dr Non updates the bible (adds a new shape, refines an anti-pattern), every future video picks up the change with no code edit.

## How the brain integration deepens it

If you also have an Obsidian vault wired in (see [`docs/10-obsidian-brain.md`](10-obsidian-brain.md)), put a richer version of these files in `~/Brain/TemporalLobe/storytelling/`:

```
~/Brain/TemporalLobe/storytelling/
├── openings-bible.md             ← canonical version, with rotation log
├── storytelling-techniques.md
├── opening-rotation-log.md       ← which shape was used in which piece
└── examples/                     ← longer excerpts from your blog
```

The skill can read from the brain instead of (or in addition to) the bundled `prompts/` files. When you publish a new piece, log which shape you used. Over time the rotation log makes overuse visible — *"I haven't used Shape 6 (parable) in 12 pieces; push for it next."*

This is the "vector" pattern Dr Non hinted at — though we're not using actual embeddings yet. It's structured retrieval: brain has the catalogue, script-drafter reads it, both stay in sync. Vector embeddings would let the drafter find the *most similar prior opening* and rotate AWAY from it; for now, the rotation rule + the catalogue is enough.

## What it looks like in production

Before this fix, an idea like *"What do you do when an old friend stops replying?"* would get drafted as:

> *"I remember standing on a Bangkok street corner one humid afternoon, when my phone buzzed with a notification — or maybe it didn't. The silence from my friend had become a kind of weather…"*

Generic. Hollywood. Not Dr Non.

After the fix:

> *"Someone asked me recently, 'What do you do when an old friend stops replying?' I thought of Chai. We used to share late-night talks, swapping dreams over cheap whiskey in a dark Bangkok bar. Then, silence. Messages sent, responses faded. Weeks turned to months."*

Shape 1 opener (People-ask-me variant), named specific person (Chai), Asia-anchored (dark Bangkok bar), Hemingway rhythm in the body. **Four techniques applied in three sentences.** That's Dr Non's voice, recovered.

## Forking for your own voice

If you fork this skill for your own use:

1. **Replace `prompts/openings-bible.md`** with your own catalogue.
   - Mine your own corpus (Step 1 above).
   - Keep the structure: 5-10 shapes, 3-4 examples per shape, anti-patterns at the bottom, rotation rule at the top.
   - Keep the FORK NOTE banner — it reminds future-you (or your team) that the catalogue is bespoke.

2. **Replace `prompts/storytelling-techniques.md`** with your own structural moves.
   - The technique categories from Dr Non's version (two-truth move, named-specific-person, etc.) won't all apply to you.
   - Read your own writing for what you do *structurally* that an LLM wouldn't invent. Those are your techniques.

3. **Update `prompts/voice-preamble.md`** with your banned-vocabulary list.
   - Look at LLM drafts of your work. Note every word you'd never use ("delve into", "embrace", "navigate" as a verb, etc.). Ban them explicitly.

4. **Don't touch `scripts/build.py`'s `load_storytelling_reference()`** — it reads whatever files you put in `prompts/`. The structure is universal.

That's it. Ten minutes of corpus mining + 30 minutes of editing the bibles + restart the skill, and your wisdom videos sound like *you* instead of like every other AI creator on TikTok.

→ Back to [`README.md`](../README.md).
