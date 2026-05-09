# Factory Floor — starter implementation

> Minimal, runnable scaffold for the executor-mode protocol described in [`../../docs/12-factory-floor.md`](../../docs/12-factory-floor.md).
>
> ~550 lines of Python total, no extra dependencies beyond `urllib` (stdlib). Drop-in alongside the existing `tiktok-wisdom` skill.

## What's here

```
examples/factory/
├── blackboard.py          ← shared JSON state store (file-backed)
├── router.py              ← Router agent — gpt-4o-mini GO/BLOCK classifier
├── workers/
│   ├── __init__.py
│   ├── script_factory.py  ← Script Factory worker — drafts segments via LLM
│   └── voice_synth.py     ← Voice Synthesizer worker — direct ElevenLabs API
└── run.py                 ← end-to-end demo orchestrator
```

The full pipeline:

1. **Router** classifies the request (task type, pipeline, auto_ship, cost estimate) and writes to the blackboard.
2. **Script Factory** reads the routing artifact + any research context, loads Dr Non's storytelling brain (`~/Brain/TemporalLobe/storytelling/`), calls gpt-4o-mini, and writes 3–10 segments to `artifacts["script"]`.
3. **Voice Synthesizer** reads `artifacts["script"]`, calls ElevenLabs with retry+fallback, writes MP3 paths to `artifacts["audio"]`.
4. All errors go to `state["errors"]` for post-hoc QA. All costs tracked in `state["cost_tracker"]`.

The storytelling brain is optional — if `~/Brain/TemporalLobe/storytelling/` isn't present, Script Factory uses a compact built-in style block. The pipeline degrades gracefully in both cases.

What's deliberately NOT here:

- A real Research worker (in production, calls Perplexity / GPT-4o + search).
- Visual Director / Video Renderer (~150 LOC each, same shape).
- Integration worker (FFmpeg concat + normalisation + tag injection + CDN upload).
- QA worker (post-hoc audit).
- Analytics agent (download-stats feedback loop).

The pattern for adding any of those: same shape as `voice_synth.py` — a single function that reads the blackboard, does its work, writes its artefact back, logs errors, ships even if degraded.

## Prerequisites

```bash
# Python 3.11+ (uses tomllib + modern syntax)
python3 --version

# Essential — Router + Script Factory:
export OPENAI_API_KEY=sk-...

# For Voice Synth (optional — pipeline degrades gracefully without these):
export ELEVENLABS_API_KEY=sk_...
export ELEVEN_VOICE_ID=<your_voice_id>
export ELEVEN_FALLBACK_VOICE_IDS=<id1>,<id2>   # optional fallback chain
```

If you don't have an ElevenLabs key, the demo still runs: Router classifies and Script Factory drafts the script, then the voice step logs "ELEVENLABS_API_KEY missing" and exits cleanly. That's the factory pattern — missing dependencies degrade gracefully, never crash.

## Run the demo

```bash
cd examples/   # NOT examples/factory — run as a module from examples/

# Full pipeline — Router → Script → Voice:
python3 -m factory.run --request "podcast ep019 about EU AI Act"

# Router-only dry-run (zero API cost beyond gpt-4o-mini classify):
python3 -m factory.run --request "podcast ep019 about EU AI Act" --dry-route

# Router + Script Factory only (see the script, skip ElevenLabs spend):
python3 -m factory.run --request "wisdom video about patience" --dry-script

# Custom project id + work dir:
python3 -m factory.run \
  --request "tiktok video about waiting" \
  --project-id v042 \
  --work-dir /tmp/factory-test
```

Expected output (`--dry-script` run):

```
[1/4] Init blackboard for project='demo001'
  ✓ blackboard at /Users/.../.openclaw/factory/demo001.json

[2/4] Router decides…
  task_type:    video
  pipeline:     video
  auto_ship:    True
  estimated:    $0.25

[3/4] Script Factory drafts script…
  segments:     4
  duration est: ~85s
  opening:      Shape 1

  Script preview:
    [intro] People ask me all the time — how do you stay patient when the
    [main] Patience isn't passive. It's the…
    [main] The Stoics called it…
    [outro] So the next time you feel the urge to rush…

=== Final blackboard state ===
  status:       scripted
  cost:         $0.0008
  api_calls:    {'openai': 2}
  errors:       0 logged
```

Full pipeline with voice adds `[4/4] Voice Synthesizer renders N segments…`.

After the run, peek at the state JSON:

```bash
cat ~/.openclaw/factory/demo001.json | jq
```

You'll see the full audit trail: routing decision, audio file paths, cost breakdown, any errors that fired. That's the "post-hoc QA" Ana would read; it's what makes the factory's reactive shipping safe.

## How to extend — adding the next worker

`script_factory.py` is already wired in. The next natural addition is a **Research worker** that fetches context before the script is drafted:

```python
# examples/factory/workers/research.py
from .. import blackboard

def fetch(project_id, topic, *, work_dir=None, perplexity_api_key=None):
    blackboard.update_status(project_id, "researching", work_dir=work_dir)

    # 1. Call your search API (Perplexity, Tavily, etc.)
    notes, usd = _call_search_api(topic, perplexity_api_key)
    blackboard.add_cost(project_id, api_call="perplexity", usd=usd,
                        work_dir=work_dir)

    # 2. Write the artefact. Script Factory will pick it up automatically.
    blackboard.add_artifact(project_id, "research",
                            {"notes": notes, "query": topic},
                            work_dir=work_dir)
    blackboard.update_status(project_id, "researched", work_dir=work_dir)
    return notes
```

Three rules every worker follows:

1. **Read the blackboard, don't pass arguments.** If you need a prior worker's output, read it from `state["artifacts"]["<key>"]`.
2. **Track every API call's cost.** `blackboard.add_cost(..., usd=...)` so the Router can enforce budget caps next time.
3. **Log errors, don't raise.** Catch exceptions, call `blackboard.log_error(...)`, fall back to a degraded output (stub notes, silence-gap audio, last-good-frame video, etc.). The pipeline ships.

## Why a JSON file instead of Redis

For one user with ~10 active projects at a time, file-based state is fine. Atomic writes via `os.replace()` survive crashes.

When you outgrow this:
- ~50 concurrent projects → swap `blackboard._read` / `_write` for Redis. Same interface; ~30 lines change.
- Multi-machine factory → SQLite with `WAL` mode, then PostgreSQL.

Don't pre-build for scale you don't have. The whole point of the factory floor is producing artefacts cheaply — that includes the infrastructure.

## Testing without burning credits

```bash
# Router-only — costs ~$0.0001 per run
python3 -m factory.run --request "..." --dry-route

# Full demo with stub segments — costs ~$0.01 (if ELEVENLABS_API_KEY set)
python3 -m factory.run --request "..." --project-id testrun
```

Inspect blackboard state between runs to see how the protocol evolves. `state["errors"]` is your friend during development — every retry, every fallback, every degraded path leaves a trace there.

## What this proves

The factory protocol is small. ~400 lines and you have a real reactive pipeline that ships even when ElevenLabs has a bad day. The hard part isn't the code — it's the *discipline* of "stateless workers, stateful board, no conversation history, ship degraded over blocking on debate."

When you migrate your daily-podcast workflow to this pattern, the chat noise we've been watching (Otto looping on retry messages, Bob debating philosophy mid-render) goes away. The pipeline does its job; the chat is for humans.

→ Architecture detail: [`../../docs/12-factory-floor.md`](../../docs/12-factory-floor.md).
→ Migration roadmap: same doc, "Migration" section.
