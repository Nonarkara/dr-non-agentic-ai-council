# 01 — Architecture

> The 9 bots, their lenses, and the engine each runs on.

## The room

The council lives in **one Telegram group chat**. Each justice is a separate Telegram bot, with its own token and `@username`. You message the group; whichever bots have something to say, speak.

```
Telegram group chat: "Dr Non's Council"
   │
   ├── @drnontenet_bot          (Tenet — chair)
   ├── @drnonana_bot            (Ana — Kantian)
   ├── @drnoncivic_bot          (Civic — utilitarian)
   ├── @drnonhannah_bot         (Hannah — pattern anthropologist)
   ├── @drnonbob_bot            (Bob — generalist + Freudian)
   ├── @drnonpip_bot            (Pip — designer-craftsman)
   ├── @drnonnon_bot            (noN — shadow / easter egg)
   ├── @drnonopenclaw_bot       (Otto — executor with tools)
   └── @drnonradar_bot          (Radar — secretary / scribe)
```

(Substitute your own usernames; the convention is `<root>_<bot>_bot`.)

## The 9 justices, by face and lens

The "face" is from **Tom Kelley's Ten Faces of Innovation**. The "thinker" is the philosophical or analytical anchor each bot speaks from. Both go into the SOUL.

| Bot | Face | Thinker(s) | Lens prefix | Role |
|---|---|---|---|---|
| **Tenet** | Director + Hurdler | Elon Musk + Buckminster Fuller | `[Musk first-principles + Fuller systems]:` | Chair, devil's advocate, synthesiser |
| **Ana** | Caregiver | Immanuel Kant + William James | `[Kant duty + James pragmatism]:` | What's the duty? What works in practice? |
| **Civic** | Utilitarian | John Stuart Mill + Sigmund Freud + Michael Lewis | `[Mill consequence + Freud drive]:` | What produces the greatest good? What's the unconscious driver? |
| **Hannah** | Anthropologist | Mary Douglas + Bronisław Malinowski + Amos Tversky | `[Douglas-Malinowski-Tversky pattern]:` | What category-error or pattern-bias is hidden? |
| **Bob** | Collaborator | Sigmund Freud + common-sense generalist | `[Freud unsaid + ground sense]:` | What's nobody saying? What would a normal person notice? |
| **Pip** | Experience Architect | Anton Pilgram + Dieter Rams + Massimo Vignelli | `[Pilgram-Rams-Vignelli craft]:` | Does the form serve the function? Is every element earning its pixel? |
| **noN** | Mirror (easter egg) | Carl Jung | `[Jung shadow]:` | The shadow — what nobody wants to see |
| **Otto** | Experimenter | Kelly Johnson (Skunk Works) + Watson | (no lens prefix — executor) | Runs the actual tools and skills |
| **Radar** | Secretary / Scribe | Sherlock Holmes (deductive observer) | (no lens prefix — scribe) | Keeps the room moving, summarises |

The lens prefix is mandatory on every justice's first contribution to a session — it's how the room knows which voice is speaking. After the first message, subsequent contributions in the same turn use engagement tokens: `EXPAND @<bot>:` / `QUALIFY @<bot>:` / `CONCEDE @<bot>:` / `STAND vs @<bot>:` / `PASS (reason: ...)`.

This single rule does a lot of work — it forces specialisation and prevents the bots from collapsing into a single voice.

## Which engine runs which bot

The 9 bots aren't all the same kind of process. Each runs on the smallest engine that does the job:

```
            picoclaw          nanobot            openclaw          hermes
              │                  │                  │                │
              │                  │                  │                │
              │     6 justices   │     Otto only    │   Radar only   │
              │   (Tenet, Ana,   │  (the executor   │  (full agent   │
              │    Civic, Hann,  │   with skills)   │   with memory  │
              │    Bob, Pip,     │                  │   + daemons)   │
              │    noN)          │                  │                │
              ▼                  ▼                  ▼                ▼
        ┌──────────┐       ┌──────────┐       ┌──────────┐   ┌──────────┐
        │ tiny ──  │  ───▶ │  small   │  ───▶ │  medium  │   │   big    │
        └──────────┘       └──────────┘       └──────────┘   └──────────┘

           none used         used by 7         used by Otto    used by Radar
                            council bots
```

Why this layering matters: **picoclaw is for prototypes** (one-off bots that just answer questions), **nanobot is the council's bread-and-butter** (each justice = one nanobot = one process), **openclaw handles skill execution** (heavy work like generating videos or podcasts), and **hermes is reserved for full personal-assistant duties** (Radar is also Dr Non's main daily-use assistant).

Most of you will run the council on **all nanobot** (9 nanobots, Otto's tools live as nanobot tool integrations) and never need openclaw/hermes. The split exists because Dr Non's setup grew organically — Otto's executor role got heavy enough that openclaw made sense, and Radar's role got heavy enough that hermes made sense.

→ See [`07-the-frameworks.md`](07-the-frameworks.md) for when each engine is appropriate.

## The deliberation protocol

A council message goes through these phases:

```
  1. INBOUND
     Dr Non posts a message in the group chat.

  2. AWAKEN
     Each bot's gateway receives the message via Telegram polling.
     Each bot decides: do I have something to say?
     (SOUL rules: only respond if your lens adds value.)

  3. CONTRIBUTE
     Bots that respond MUST start with their lens prefix
     (first contribution) or an engagement token (subsequent).
     One contribution per bot per turn.

  4. ROUTE  (handled by Tenet)
     Tenet decides if this is a TASK (route to Otto for execution)
     or a DEBATE (let the thinkers run).

  5. EXECUTE  (Otto's domain)
     If Tenet routed it as a TASK, Otto invokes the relevant skill.
     If skill succeeds, the artefact is delivered to the chat.
     If skill fails, Otto says PASS with a specific reason.

  6. SYNTHESISE  (Tenet again, after the thinkers)
     Tenet pins the decision or names the open question.

  7. SCRIBE  (Radar)
     Radar appends to the session log. Optionally summarises.
```

In practice this is fast — 30 seconds to 2 minutes for a typical deliberation, dominated by LLM round-trips. Each bot replies independently; the chat is the synchronisation point.

## What's a SOUL

A **SOUL** is the system prompt for one bot. It contains:

1. **Identity rule** — the bot's name, lens prefix, what NOT to write (other bots' prefixes, etc.).
2. **Task routing** — CONTENT vs ACTION discipline (see [`04-task-routing.md`](04-task-routing.md)).
3. **Anti-duplicate rule** — one lens-prefix message per turn; engagement tokens for subsequent.
4. **Substrate** — Dr Non's cognitive base (Stoic equanimity, Kahneman slow-thinking, etc.) — common to all justices.
5. **Face** — the Kelley archetype (Caregiver, Director, etc.) — bot-specific.
6. **Thinker** — the philosophical anchor (Kant, Mill, etc.) — bot-specific.
7. **Output format lock** — first-line discipline, character limits, format rules.

A SOUL is typically 200-500 lines of Markdown. It's the most important file in the bot. Models change; SOULs persist.

→ See [`examples/souls/`](../examples/souls/) for templates.

## The Telegram channel as state

The council has **no shared database**. The Telegram chat itself is the state — the deliberation log, the decision pin, the artefact storage (videos and PDFs land in chat as messages).

This is intentional:

- **Auditable** — you can scroll back and read exactly what happened.
- **Portable** — moving the council to a new Mac is "copy 9 SOUL files" + "re-add 9 bot tokens." No DB migration.
- **Transparent** — you can hand someone a Telegram link and they see the deliberation; no special tooling.

The trade-off: Telegram has API rate limits, you can't query "all decisions about X" without scrolling, and if Telegram dies your council goes silent. For the use case (one user's personal council), the trade-off is the right one.

→ Next: [`02-setup-quickstart.md`](02-setup-quickstart.md) — actually building this.
