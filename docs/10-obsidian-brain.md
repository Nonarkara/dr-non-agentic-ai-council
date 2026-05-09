# 10 — The Obsidian Brain (long-term memory for the council)

> The chat is the council's working memory. The Obsidian vault is its long-term one.

The council in Telegram is *fast* — questions in, lenses out, decisions pinned. But Telegram is bad at **remembering across days**. Scroll back ten weeks and you can't find the decision Tenet pinned about that contract; the chat is a stream, not a library.

The Obsidian vault solves that. Every council session of consequence ends up persisted as a Markdown file in a brain-anatomy folder structure. The thinkers can read it, write to it, and recall the past when a similar question comes back.

## Two implementations

Dr Non runs two complementary brain repos. Use the one that fits your workflow:

| Repo | What | When to use it |
|---|---|---|
| **[`agentic-ai-research/brain-vault`](https://github.com/agentic-ai-research/brain-vault)** | Pure Obsidian vault — folders of `.md` files, brain-anatomy structure (Amygdala, Hippocampus, Cerebellum, FrontalLobe, etc.). Read and edit in Obsidian. | You live in Obsidian. You want full local control. You like the linking + graph-view side of Obsidian. |
| **[`Nonarkara/second-brain-v2`](https://github.com/Nonarkara/second-brain-v2)** | Next.js dashboard reimplementation — webapp with multi-bot Telegram support, neural-memory UI, dashboard. | You want a web UI on top of the brain. You want the brain accessible from any device, not just where Obsidian is installed. |

Both share the same conceptual structure (folders mapped to brain regions). You can use them in parallel — the Next.js app reads from the Obsidian vault filesystem, so changes in either propagate.

## The brain-anatomy folder structure

```
~/Brain/
├── Amygdala/         # emotional memory — feelings, interpersonal moments
├── Brainstem/        # autonomic — heartbeat, automated processes
├── Cerebellum/       # motor memory — muscle-memory routines, daily habits
├── CorpusCallosum.md # cross-hemisphere index
├── Council/          # ← council session transcripts and pinned decisions
├── FrontalLobe/      # planning, executive function — strategic notes
├── Hippocampus/      # episodic memory — what happened when
├── Hypothalamus/     # drives — what you actually want vs what you say
├── Inbox/            # raw capture, unsorted
├── Index.md          # master index
├── Markets/          # finance, trades, watch lists
├── OccipitalLobe/    # visual — diagrams, screenshots
├── ParietalLobe/     # spatial — places, travel, geography
├── PrefrontalCortex/ # the thinker's notebook — drafts, working theories
├── Projects/         # active work
├── Synapse/          # connecting notes — link-only files
├── Templates/        # Obsidian templater for new notes
└── TemporalLobe/     # long-term semantic memory — books, blog corpus
```

The metaphor isn't strict science — it's a memory system. Each folder has a role you can teach to the bots.

## How the council reads + writes the brain

The council uses three patterns to interact with the vault:

### 1. Council session → `Council/`

After every consequential council turn, Radar (the secretary) appends a session log to `~/Brain/Council/sessions/YYYY-MM-DD-<slug>.md`. The log includes:
- The question Dr Non asked
- Each justice's lens-prefixed contribution
- Tenet's synthesis / the pinned decision
- Any artefacts Otto produced (with paths)

This is automatic — Radar's hermes config has a daemon that watches the council group chat and writes sessions as they happen.

### 2. Skill → brain folders

Skills that produce content drop the artefacts into the right brain region:
- `tiktok-wisdom` saved videos → `~/Brain/OccipitalLobe/wisdom-videos/`
- `blog-to-podcast-pipeline` MP3s → `~/Brain/TemporalLobe/podcasts/`
- `card-to-google-contact` OCRed cards → also linked into `~/Brain/Hippocampus/people/<name>.md`
- Daily retrospective → `~/Brain/Council/retrospectives/YYYY-MM-DD.md`

The pattern: **skills know which folder their output belongs in**. The skill's SKILL.md declares its target.

### 3. Bots reading the brain at deliberation time

A justice's SOUL can include a directive like:

```
## CONTEXT FETCH

Before responding, if the question references a past decision, search
~/Brain/Council/ for related sessions and quote ≤ 3 sentences from the
most relevant one.
```

This works on any bot whose engine has filesystem tools (nanobot with file-tool enabled, openclaw, hermes). picoclaw can't do it — too small.

In practice, **Radar does most of the brain-recall work** because hermes has the heaviest tool stack. The reasoning bots just deliver their lens; Radar surfaces the past.

## The "Brain skills" — openclaw skills that touch the vault

| Skill | What it does |
|---|---|
| `brain-ingest` | Email → relevant brain folder. Watches Gmail for tagged emails, parses, files them. |
| `tripit-watcher` | Travel reservation → `~/Brain/ParietalLobe/travel/<trip>.md`. |
| `daily-retrospective` | At 23:55 Bangkok, reads the day's council messages and drafts `~/Brain/Council/retrospectives/<date>.md`. |
| `brain-search` | Full-text search across the vault, ranks by recency + folder weight. Otto can call this. |
| `brain-link-graph` | Generates a Mermaid graph of links between recent notes — debugging tool. |

(Some of these live in this repo's sibling `dr-non-diy-ai-council` skills folder; some are private to Dr Non's local openclaw install.)

## How second-brain-v2 (the Next.js app) plugs in

`Nonarkara/second-brain-v2` is a separate webapp that **reads the same Obsidian vault** as files. Specifically:

```
second-brain-v2/
├── app/                  # Next.js routes — /dashboard, /memory, /bots
├── components/           # React components for the memory views
├── lib/
│   ├── vault.ts          # reads ~/Brain/*.md (or a remote-mounted vault)
│   ├── bots.ts           # Telegram multi-bot support
│   └── neural-memory.ts  # the "Living Brain" pattern — graph of notes by recency
└── hooks/                # React hooks — useVault, useBots, useMemory
```

Run it locally with `npm run dev`, point it at your `~/Brain/`, and you get a dashboard that:
- Shows the council's recent decisions (reads `~/Brain/Council/`)
- Lets you ask the bots from a web UI (proxies to the Telegram bot APIs)
- Visualises the memory graph
- Provides a webhook layer for Telegram bot integration that's separate from your local nanobots

It's optional. The pure Obsidian + Telegram setup works fine without it. Use second-brain-v2 when you want the brain accessible from a phone or browser without opening Obsidian.

## Privacy and "Peter's brain"

Dr Non's setup has two human users — Dr Non himself and Peter Karl (his collaborator). Each has a separate vault root:

```
~/Brain/                  # Dr Non's vault
~/PeterBrain/             # Peter's vault (when running on Peter's machine)
```

The bots' SOULs include a `TWO HUMAN USERS` block that detects which user the inbound message is from and routes brain reads/writes to the right vault. See [`examples/souls/Bob.SOUL.md`](../examples/souls/Bob.SOUL.md) for the routing pattern (search for `TWO HUMAN USERS`).

If you fork the council for solo use, simplify by removing the user-detection logic and pointing all brain ops at one `~/Brain/`.

## Setup checklist

To wire the brain into the council:

1. **Pick which vault repo to clone:**
   ```bash
   # If you want pure Obsidian:
   git clone https://github.com/agentic-ai-research/brain-vault.git ~/Brain

   # OR if you want the dashboard webapp:
   git clone https://github.com/Nonarkara/second-brain-v2.git ~/Projects/second-brain-v2
   ```
   (Or fork your own.)

2. **Open the vault in Obsidian** (download from https://obsidian.md, free for personal use).

3. **Enable filesystem tools in your council bots:**
   - For nanobots: in `config.json`, ensure `tools.file` is enabled.
   - For openclaw (Otto): the brain skills come pre-wired.
   - For hermes (Radar): the brain folder is in the default toolset's `read_path` allowlist.

4. **Tell each bot where the brain lives:**
   - Add to each SOUL: `## BRAIN PATH\nYour brain vault is at \`~/Brain/\`. Use it for context retrieval and decision logging.`

5. **Test recall:**
   In the council group, post: *"What did we decide about X last month?"* — Radar should search the vault and surface the relevant session.

## When to NOT use a brain

If you're prototyping the council, skip this. The vault is overhead — you have to maintain folder structure, occasionally clean up stale notes, and worry about sync if you run on multiple machines. **Build the council first, the brain second.**

The brain pays off after ~3-4 weeks of council use, when there's enough accumulated state that recall becomes valuable. Before that, the chat itself is enough memory.

→ Back to [`README.md`](../README.md).
