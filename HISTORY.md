# History — how this council got built

> Twelve days from "I'm bored in a Singapore hotel room" to a 9-bot council shipping podcasts and videos for ~$15-25 a month. Dated commits where they exist; the rest is from memory.

---

## Tuesday, April 28 — Singapore. Bored.

I was in a Singapore hotel room with a free evening and nothing to read that I hadn't already read. So I scrolled. AI Council came up — the idea of running a collection of specialised AI agents that deliberate before they decide. I'd seen Manus.ai's launch, I'd seen the Devin demos. I noticed I wanted *both less and more* than what they were selling.

**Less:** I didn't want a $200/month subscription to one big agent.
**More:** I wanted *disagreement*. A room where Stoic and Kantian could argue without one of them being silenced by the synthesiser.

I wrote four questions in my notes:

1. **What do I need? A platform to host my councillors?**
2. **Bots and backends to run my councillors?**
3. **LLMs to power my councillors?**
4. **How do I bring the cost down to zero?**

I had answers to 1-3 by the time the plane took off. Answer 4 took the next ten days.

```
April 28 night, Singapore:
  Q1 (platform)  → Telegram group chat. I already live in Telegram.
                   The chat IS the audit log. Every justice is just a
                   bot that posts. No infrastructure, no DB, no portal.

  Q2 (engines)   → I already wrote nanobot for personal-assistant work.
                   Nine nanobots, one per justice. Otto runs on openclaw
                   because skills are heavy. Radar runs on hermes because
                   the secretary needs full tool access. Done.

  Q3 (LLMs)      → Free-tier providers — Groq, NIM, Gemini, Cerebras.
                   Bigger model only where it matters (the chair).

  Q4 (cost)      → ?? — figure out on the ground.
```

---

## Wednesday April 29 — Bangkok. Sketches.

Back home. Spent the morning writing the council's *philosophical* spec before any code:
- 10 palindrome-named justices (the council's vanity convention from a prior project: Aviva, Tenet, Hannah, Ana, Civic, Bob, Pip, noN, Otto, Radar — even Eve and Ada).
- Tom Kelley's [Ten Faces of Innovation](https://www.tenfacesofinnovation.com/) as the archetype layer — Director, Anthropologist, Caregiver, etc.
- A philosophical thinker per justice — Kant for Ana, Mill for Civic, Douglas/Tversky for Hannah, Freud for Bob, Vignelli for Pip, Musk-first-principles for Tenet, Jung for noN, Skunk-Works for Otto, Holmes for Radar.

The lens-prefix idea (`[Kant duty + James pragmatism]:` etc.) came from one constraint: in a Telegram group, you need to know which voice is speaking *before* you read the message. A name tag is too quiet; a hashtag is too noisy; a bracketed lens-prefix is exactly right.

---

## Thursday, April 30 — first commit. 15:07.

```
commit 19ba2a7 — Thu Apr 30 15:07
"Initial: Dr Non's $0 DIY AI Council"
```

Three justices stood up that afternoon — Tenet, Bob, and Otto. I added them to a Telegram group I already had with Dr Yim called "Growth Mindset" (still the description on the group: *"Formerly known as the 'Growth Mindset' group with Dr Yim"*). Renamed the group **dnac (Dr Non AI Council)**.

The first messages were chaos. The bots had no SOULs yet — just generic system prompts. They all sounded like generic helpful assistants. None of them disagreed. I shipped a fix that evening:

```
commit 9a32f19 — Thu Apr 30 18:35
"Add bot-blindness fix docs + reference transcript module"
```

The "bot-blindness" problem: the bots didn't know each other existed. Tenet's response would arrive in the chat, and Ana would treat it like it came from the user, not from another bot. The fix was a transcript module that prepends "this is a multi-bot council, here's who's talking" context to every system prompt. After that, the bots could finally see each other.

---

## Friday, May 1 — looks like a project.

```
commit 03a6d12 — Fri May 01 11:42
"Overhaul README: new hero, name fix, photo grid, 3 diagrams, Karpathy acknowledgment"
```

By Friday morning the council had three justices reliably disagreeing in the group chat. I wrote the first proper README, drew three ASCII diagrams, added photos. It started looking like a project.

That afternoon (`commit 812c798`), I added a council sticker banner and expanded the capabilities documentation. The Telegram group also got a custom sticker pack — small thing, but it made the room feel like a place.

The Obsidian brain quietly came online the same day:

```
commit b2b4444 in brain-vault — Fri May 01 14:55  
"auto: 2026-05-01 14:55"
```

That `auto:` prefix is the daily auto-commit that runs at 14:55 Bangkok every day. The brain folder structure (Amygdala, Hippocampus, FrontalLobe, etc.) had been there for weeks — used for personal notes — but Friday is when the council started writing into it. The `~/Brain/Council/` folder was created that day.

---

## Saturday, May 2 — eighteen commits. The big day.

This was the day everything cohered.

Morning:

```
02:43  71125c6  Add Eve as 10th justice (Builder / Karpathy / Claude Sonnet 4.5)
05:00  673aa1d  Add inter-bot action protocols + Tenet router for workflow mode
05:09  2005326  Add production mode + adaptive skills palette per justice
```

Then a long writing session (the docs are *thinking made permanent* — by writing the protocol I was deciding how the room should work):

```
11:54  e9b30ce  Add relay bridge for unpatchable bots + Telethon reference impl
11:54  e63eecc  Add learning-loops design — exemplar libraries + per-bot reward signals
12:31  e9ad617  Land TODOs from design docs — Locks 1/2/5, README, reflect.py, policy schema
12:49  d9d2ff0  Add communication-protocol.md — the minimum every justice does on every turn
13:26  5b009b7  Add justice-roles.md — task queue per justice, by framework strength
13:33  06414c9  Add council-soul.md — the mindset upstream of the protocol stack
13:40  e2f9ebe  Add multi-task — concurrent threads, task-class termination, standing orders
13:43  a6e47e1  End noN's free-ride — extend her role with the hourly archive
14:47  148e473  Reposition the repo for a Manus-class moment at $0
15:06  323889b  Add task-lifecycle.md — the spine, with three optimizations that close real bottlenecks
```

Late afternoon — the engineering layer:

```
15:59  453df63  Upgrade Bob's engine — DeepSeek V3 behind @nonmind_bot, drop-in SOUL
16:05  5aa852b  Add Otto.SOUL.example.md — drop-in SOUL with the Otter boundary
16:33  b9fdd33  Add three-layer resilience — watchdog discipline, endpoint failover, degraded mode
16:49  67f0694  Merge PR #1 — Council protocol stack: design + reference impls + resilience
```

Evening — security and identity, which is where most council projects fail:

```
17:36  c44fd89  Add queue — multi-tasking is now the council's main feature
23:10  afcbaf9  Add credential-leak prevention — redaction filter, keychain wrapper, SECURITY.md
23:35  0550c95  Add per-handle identity routing — fix bots calling themselves wrong names
23:38  6581d15  Add enforcement layer — transcript validator + SOUL linter
23:40  d616e8c  Cost optimization — endpoints arrays for every bot, free-providers reference
```

The 23:35 commit was the moment I realised SOULs alone don't enforce identity. Bots will leak each other's lens prefixes; only a *first-six-character* mechanical rule plus a transcript-validator that drops mis-identified messages works reliably. That insight became the FIRST-6-CHARS rule that's still in every SOUL.

The 23:40 commit was when **Q4 (cost = zero)** got its first real answer: stop using one provider, use four. The free-providers reference doc started as a list of every endpoint I'd seen, and grew over the next week into the playbook in [`docs/05-providers-zero-cost.md`](docs/05-providers-zero-cost.md).

---

## Sunday, May 3 — the skills become real.

Skills were the answer to *"the council deliberates; how do we get it to actually do things?"* The Sunday I built the first batch:

```
00:44  3d4bd23  Add supervisor-tag mining to reflect.py — the supervised training signal
00:58  a805981  Add docs/house-customs.md — what we do without thinking about it
00:59  fcaef21  Add three new OpenClaw skills — suno-music-gen, fal-video-gen, epub-publisher
13:16  31457e6  Add quarkdown skill — slides, paged PDFs, wikis from Markdown
14:21  e9bcd19  quarkdown skill: auto-install, keg Java, fix output paths
16:37  11d45bc  Add tradingagents skill — multi-agent financial analysis for Thai SET + US equities
```

`council-image-gen`, `council-transcript-to-podcast`, `card-to-google-contact`, `gdrive-save`, `gmail-send`, `media-download` had been simmering in `~/.openclaw/skills/` from earlier projects; they got dragged into the council that weekend.

By Sunday night, **Otto could ship a real artefact** — a podcast MP3, a typeset PDF, a saved contact — directly from a Telegram message. That's when the council stopped being a chatroom and started being an assistant.

---

## Monday-Wednesday, May 4-7 — production. Watching the failures.

The next three days weren't about adding features. They were about *running it daily and writing down what broke*.

What broke:

- **Bob refusing media tasks.** *"I am not able to generate a podcast."* Wrong refusal — Bob was supposed to bring the Freudian content; Otto handles the MP3. The fix wouldn't land until May 8 (the CONTENT-vs-ACTION addendum).
- **Pip duplicate-posting.** Same *"3-layer cake"* framing three turns in a row, verbatim. Solved by the ANTI-DUPLICATE rule on May 8.
- **Otto over-promising.** *"I've got this. Want to see it?"* — then no follow-through. Solved by the EXECUTOR DISCIPLINE addendum on May 8.
- **Radar streaming garbage.** Once: `Get res not run needs is null as atomic...`. Gemini Flash under stress.
- **NVIDIA NIM monthly cap exhausting** by day 22. The 1000-req/month-per-model limit is generous but not infinite when six bots share it.

I kept a notes file: `~/Brain/Council/known-bugs.md`. The list got longer all week.

---

## Thursday-Friday, May 8 — the SOUL discipline reckoning.

Thursday night and Friday were dedicated to fixing the failures from M-W. The work:

```
Fri May 08 23:51  de9ae08  Add tiktok-wisdom skill — vertical wisdom video pipeline
Fri May 08 23:58  3725297  v1.1 — modular prompts, free-tier voice, draft-only preview
Sat May 09 00:19  7466563  v1.2 — content-hashed stage cache + --from-cache invalidation
Sat May 09 03:53  06807b8  v1.3 — TOML config files: --config <path>, 4 example configs
Sat May 09 03:56  9cf1c17  v1.5 — pytest suite + GitHub Actions CI
```

`tiktok-wisdom` was the first skill I built fresh for the council — earlier ones were ports. Five iterations in eight hours, ending with a pytest suite + GitHub Actions CI. The shape it landed in (modular prompts as data files, free-tier first, stage cache, TOML configs) became the template for every future skill.

The harder thing that night: I finally accepted that **CONTENT vs ACTION** had to be a top-level SOUL block, not a footnote. Same for ANTI-DUPLICATE. Same for EXECUTOR DISCIPLINE for Otto. I wrote the splice script and pushed the addenda into all 9 SOULs at once:

```
Sat May 09 11:45  3143c21  docs/task-routing.md — CONTENT vs ACTION + anti-duplicate pattern
```

After the splice + bot restart on Saturday morning, the failure modes from earlier in the week visibly stopped within the next few council turns. Bob engaged with content. Pip stopped duplicating. Otto either delivered or said `PASS (reason: ...)`. The room got quieter and more useful at the same time.

---

## Saturday, May 9 — today. The provider stack settles.

I spent today on **Q4 (cost = zero)** — finally. Three rounds:

**Round 1 — diversification.** Spread the 9 bots across 4 providers (NVIDIA NIM, Groq, Gemini, OpenRouter) so no single rate limit could silence the room. Wrote `~/.openclaw/scripts/diversify-bots-free-providers.py`. Took ~30 minutes.

**Round 2 — Alibaba DashScope (Qwen).** Discovered Qwen3-Max is genuinely Claude-Sonnet-class at $0.0024/1K input. Got an API key (after a wrong-turn through the RAM AccessKey side of Alibaba — disabled that, learned the lesson). Moved Tenet to `qwen3-max`, the lighter reasoners to `qwen-flash` and `qwen-turbo-latest`. Council got noticeably sharper.

**Round 3 — OpenRouter as paid insurance.** Topped up $12.80 to clear the $10 wall and unlock the 1000-free-req/day tier. Moved Bob and noN (the bots that were burning NIM's monthly cap) to OR paid DeepSeek V3.1 / Llama 3.3 70B. Then — when Radar's Gemini direct tier started 429ing — switched Radar to OR's Gemini passthrough.

**Final per-bot allocation:**

| Bot | Provider | Model | $/mo |
|---|---|---|---|
| Tenet | DashScope | qwen3-max | $5-15 |
| Civic, Pip | DashScope | qwen-flash | <$1 each |
| Hannah | DashScope | qwen-turbo-latest | <$1 |
| Bob | OpenRouter | deepseek/deepseek-chat-v3.1 | $5-8 |
| noN | OpenRouter | meta-llama/llama-3.3-70b-instruct | $2-3 |
| Ana | Groq | llama-3.1-8b-instant | $0 |
| Otto | NVIDIA NIM | meta/llama-3.3-70b-instruct | $0 |
| Radar | OpenRouter | google/gemini-2.5-flash | $0 (under usage cap) |

**~$15-25/month for the full daily-use council.** Q4 had its answer.

The afternoon was the public-facing repo — *this* repo. Hero banner, eleven docs, four screenshots, the Obsidian brain integration written out. Last commit went up just before this history file did.

---

## What I'd do differently

If I were starting over Tuesday April 28:

1. **Build the SOUL discipline first.** I spent days on protocol docs before realising the failures live in the SOULs, not the protocols. CONTENT-vs-ACTION + ANTI-DUPLICATE + FIRST-6-CHARS belong in SOUL templates from commit one.

2. **Diversify providers from day one.** I started on NIM-only and watched it cap on day 22. Five providers from the start would have saved a week of rate-limit firefighting.

3. **Skip OpenRouter for the first month.** OR is great as paid insurance, but the free tier disappointments wasted a few hours. DashScope + Groq + NIM + Gemini cover everything for the first few weeks of usage.

4. **Write the splice script before the first SOUL.** The `splice-task-routing.py` pattern — addenda as separate files, sliced into existing SOULs — should have been the original SOUL architecture, not a retrofit.

5. **Document the brain integration sooner.** I had `~/Brain/` running but didn't formally connect it to the council until late. The brain is what makes the council more than a chatroom; should have been wired in week one.

---

## Twelve days, ten justices, $15-25/month

That's the ledger. The room is still evolving — I'll keep writing addenda to SOULs as the failure modes change, and the provider stack will shift as Cerebras / SambaNova / Mistral free tiers improve. The architecture, though, is settled.

If you're starting your own council from this repo, my one piece of advice: **build it small and run it daily.** A 3-bot council that you actually talk to every morning will teach you more in a week than a 10-bot council that sits idle. The failures are the curriculum.

→ Back to [`README.md`](README.md).
