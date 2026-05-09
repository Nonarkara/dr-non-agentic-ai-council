# 07 — picoclaw / nanobot / openclaw / hermes — when to use each

> Pick the smallest engine that does the job. Don't run hermes when picoclaw will do.

The council uses four open-source engines Dr Non maintains. Each handles a different *scale* of work. The mistake to avoid: using the heaviest engine for every bot. Most justices should be nanobots. Only Otto needs openclaw. Only Radar needs hermes.

```
                  more moving parts ──────────────────────────────────────────►

  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ picoclaw │ →  │ nanobot  │ →  │ openclaw │ →  │  hermes  │
  └──────────┘    └──────────┘    └──────────┘    └──────────┘
   one job          one bot          skills          full agent
   no tools         light tools      heavy work      long memory

   prototypes      6 council        Otto            Radar +
                   justices                         personal
                                                    assistant

  cheaper, simpler ◄────────────────────────────────────────── more capable
```

## picoclaw — the prototype shell

**Use it for: testing a new bot personality without committing.**

picoclaw is the smallest possible bot framework. One Python file, ~200 lines. It does:
- Polls Telegram for messages.
- Sends each message to an LLM with a system prompt loaded from a file.
- Posts the LLM's response back.

It does NOT do:
- Tool calling. No file access, no web search, no calendar.
- Memory. Each turn is a fresh context.
- Skill execution.

**When to use it:**
- You're prototyping a new bot's voice. Run picoclaw, edit the system prompt, talk to it, edit again. Iterate at zero infrastructure cost.
- You want to fork the council into a new context (e.g. *"council-for-product-decisions"*) and need to test the personality before scaling up.
- You're explaining the architecture to someone — picoclaw is small enough to read in 10 minutes.

**When to outgrow it:**
- The bot needs tool access (web search, file ops). → move to nanobot.
- The bot needs to remember anything. → nanobot or hermes.

→ [github.com/nonarkara/picoclaw](https://github.com/nonarkara/picoclaw)

---

## nanobot — the council's bread-and-butter

**Use it for: each council justice that's not an executor.**

nanobot is what 7 of the 9 council bots run on (everyone except Otto and Radar). It does:
- Polls Telegram for messages.
- Loads a SOUL.md as system prompt.
- Routes via litellm to ~10 LLM providers (`groq/...`, `openrouter/...`, `dashscope/...`, `nvidia_nim/...`, `gemini/...`, `openai/...`, `anthropic/...`, `deepseek/...`, `vllm/...`, `zhipu/...`).
- Tool calling: light tools (file read, web search via Firecrawl, terminal exec — opt-in per bot).
- Per-session memory.
- Telegram channels: groups, DMs, allowlist filtering.
- Cron jobs (the heartbeat for proactive bots).
- Audit logs of every turn.

It does NOT do:
- Heavy skill execution (running an `ffmpeg` pipeline takes minutes — would block the bot's response loop). → openclaw for that.
- Long-term memory across sessions, MCP server integration, daemons. → hermes.
- Multi-process orchestration (each nanobot is one process; there's no leader-of-nanobots). → the orchestrator pattern lives in hermes/openclaw.

**When to use it:**
- One justice = one nanobot process. Standard pattern.
- A specialised side-bot (e.g. `eve-coder` for coding work) that needs light tools and its own SOUL.

**When to outgrow it:**
- Tool calls take >30 sec (skill territory). → move that work to openclaw.
- Need cross-session memory (remember decisions across days). → hermes.

→ [github.com/nonarkara/nanobot](https://github.com/nonarkara/nanobot)

---

## openclaw — the skill runner

**Use it for: Otto + heavy/recurring work via skills.**

openclaw is a *skill runner*. A skill is a self-contained piece of work — a Markdown SKILL.md describing it + a Python script that does it. Examples in Dr Non's setup:

| Skill | What it does |
|---|---|
| `tiktok-wisdom` | One idea → 60-90s vertical TikTok video (Met art + ElevenLabs voice + ffmpeg). |
| `blog-to-podcast-pipeline` | Blog post URL → polished MP3 podcast with two AI hosts. |
| `council-image-gen` | Council message → DALL-E or Flux cover image. |
| `pdf-publisher` | Markdown → typeset PDF book via Quarkdown. |
| `epub-publisher` | Markdown → Apple-Books-grade EPUB. |
| `card-to-google-contact` | Business card photo → Google Contact entry via OCR. |
| `gdrive-save` | Any file in chat → saved to Google Drive with metadata. |
| `gmail-send` | Draft email → sent via Gmail API. |
| `media-download` | Instagram/YouTube/TikTok/LinkedIn URL → MP4. |
| `calendar-sync` | TripIt → Google Calendar entries. |

Each skill runs as a subprocess — slow tasks don't block the bot. openclaw orchestrates: receives a request, picks the skill that matches, invokes the skill, posts the result back to the chat.

**When to use it:**
- Otto. He has skill-execution as his entire job.
- A workshop / publishing bot that runs heavy pipelines.

**When to outgrow it:**
- You need a fully autonomous personal assistant with daemons, MCP servers, cross-session memory. → hermes.
- The skill is so light it should just be a tool call inside a nanobot. → don't add an openclaw process.

→ [github.com/nonarkara/openclaw](https://github.com/nonarkara/openclaw)

---

## hermes — the personal assistant

**Use it for: Radar + your daily personal assistant.**

hermes is the heavy one. It's a full agentic gateway:

- Big-context model handling (1M token windows).
- ~20 built-in toolsets: brain (memory), browser, code-execution, cronjob, delegation, file, image-gen, memory, messaging, session-search, skills, terminal, todo, tts, vision, web, plus optional homeassistant, qqbot, signal, slack.
- MCP servers (Anthropic's Model Context Protocol) — wire in any MCP-compatible tool.
- Daemons that watch for events (incoming emails, calendar updates, GitHub PR notifications) and act.
- Long-term memory across sessions and devices.
- Multi-modal: vision, voice, file uploads, image generation.
- Web dashboard for inspecting state.

In Dr Non's setup, hermes is **Radar** (council secretary + Dr Non's main daily-use assistant). It's significantly heavier than nanobot — uses 5-10× the tokens per turn — so reserve it for one or two roles where the depth matters.

**When to use it:**
- Your council secretary (Radar).
- Your personal assistant (the one bot you actually want to think about your week, not just answer one question).
- Anything that needs MCP server integration, daemons, or cross-session state.

**When to NOT use it:**
- Don't run a 9-bot council on hermes. The token budget will explode.
- Don't use it for a single-purpose bot. picoclaw or nanobot will do.

→ [github.com/nonarkara/hermes](https://github.com/nonarkara/hermes)

---

## The decision tree

```
Does this bot need heavy skill execution (ffmpeg, multi-step pipelines, ~minutes)?
├── yes → openclaw
└── no
    │
    Does this bot need cross-session memory, daemons, or MCP servers?
    ├── yes → hermes
    └── no
        │
        Does this bot need ANY tools (file, web, calendar)?
        ├── yes → nanobot
        └── no → picoclaw
```

For 95% of council bots: **nanobot**.
For Otto-style executors: **openclaw**.
For Radar-style scribes-with-tools: **hermes**.
For prototyping new personalities: **picoclaw**.

## How they integrate

The four engines don't know about each other directly. They integrate via:

1. **The Telegram chat itself.** All bots post to the same group. They read each other's messages. The chat is the bus.
2. **Shared SOUL conventions.** Every bot uses the lens-prefix system (see [`04-task-routing.md`](04-task-routing.md)). The protocol is in the SOULs, not the engines.
3. **The `delivery-queue`** — a small file-based queue (in `~/.openclaw/delivery-queue/`) where bots can hand off artefacts. Otto writes a generated MP3 there; the openclaw daemon picks it up and posts to chat.

That's it. No central orchestrator, no message bus, no state DB. The Telegram chat is the integration.

→ Next: [`08-skills.md`](08-skills.md) — what openclaw can actually do.
