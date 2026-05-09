# Factory Floor — starter implementation

> Minimal, runnable scaffold for the executor-mode protocol described in [`../../docs/12-factory-floor.md`](../../docs/12-factory-floor.md).
>
> ~400 lines of Python total, no extra dependencies beyond `urllib` (stdlib). Drop-in alongside the existing `tiktok-wisdom` skill.

## What's here

```
examples/factory/
├── blackboard.py          ← shared JSON state store (file-backed)
├── router.py              ← Router agent — gpt-4o-mini classifier
├── workers/
│   ├── __init__.py
│   └── voice_synth.py     ← Voice Synthesizer worker — direct ElevenLabs API
└── run.py                 ← end-to-end demo orchestrator
```

That's the smallest end-to-end shape that proves the protocol works:

- Router classifies a request and writes a routing decision to the blackboard.
- The blackboard is a simple JSON file — no Redis, no DB, no Telegram chat.
- Voice Synthesizer reads its task from the blackboard, calls ElevenLabs directly with retry+fallback, writes audio paths back to the blackboard.
- All errors go to `state["errors"]` for post-hoc QA.
- All API costs are tracked in `state["cost_tracker"]`.

What's deliberately NOT here:

- A real Research worker (in production, calls Perplexity / GPT-4o + search).
- A Script Factory that writes the segments (this demo hardcodes two stub segments).
- Visual Director / Video Renderer (~150 LOC each, same shape).
- Integration worker (FFmpeg concat + normalisation + tag injection + CDN upload).
- QA worker (post-hoc audit).
- Analytics agent (download-stats feedback loop).

The pattern for adding any of those: same shape as `voice_synth.py` — a single function that reads the blackboard, does its work, writes its artefact back, logs errors, ships even if degraded.

## Prerequisites

```bash
# Python 3.11+ (uses tomllib + modern syntax)
python3 --version

# These two env vars are essential:
export OPENAI_API_KEY=sk-...
export ELEVENLABS_API_KEY=sk_...
export ELEVEN_VOICE_ID=<your_voice_id>

# Optional but recommended — fallback voice chain for graceful degradation:
export ELEVEN_FALLBACK_VOICE_IDS=<id1>,<id2>
```

If you don't have an ElevenLabs key, the demo still runs — it'll just log "ELEVENLABS_API_KEY missing" and exit cleanly without invoking the worker. That's the factory pattern: missing dependencies degrade gracefully; they don't crash.

## Run the demo

```bash
cd examples/factory

# Full pipeline — Router decides, Voice worker runs:
python3 -m factory.run --request "podcast ep019 about EU AI Act"

# Router-only dry-run (no API spend on workers):
python3 -m factory.run --request "podcast ep019 about EU AI Act" --dry-route

# Custom project id + work dir:
python3 -m factory.run \
  --request "tiktok video about waiting" \
  --project-id v042 \
  --work-dir /tmp/factory-test
```

Expected output:

```
[1/3] Init blackboard for project='demo001'
  ✓ blackboard at /Users/.../.openclaw/factory/demo001.json

[2/3] Router decides…
  task_type:    podcast
  pipeline:     podcast
  auto_ship:    True
  estimated:    $0.50

[3/3] Voice Synthesizer renders 2 segments…
  rendered: 2/2 segments
  voice:    primary

=== Final blackboard state ===
  status:       voiced
  cost:         $0.0142
  api_calls:    {'openai': 1, 'elevenlabs': 2}
  errors:       0 logged
```

After the run, peek at the state JSON:

```bash
cat ~/.openclaw/factory/demo001.json | jq
```

You'll see the full audit trail: routing decision, audio file paths, cost breakdown, any errors that fired. That's the "post-hoc QA" Ana would read; it's what makes the factory's reactive shipping safe.

## How to extend — adding the next worker

The pattern is consistent. Here's the shape for a Script Factory worker:

```python
# examples/factory/workers/script_factory.py
from .. import blackboard

def draft_script(project_id, topic, *, work_dir=None,
                 openai_api_key=None, segments_target=4):
    blackboard.update_status(project_id, "scripting", work_dir=work_dir)

    # 1. Read research artefact (if a Research worker ran already)
    state = blackboard.read(project_id, work_dir=work_dir)
    research = state["artifacts"].get("research", {})

    # 2. Call your LLM. Track cost.
    segments = _call_llm_for_segments(topic, research, openai_api_key)
    blackboard.add_cost(project_id, llm_tokens=..., usd=..., work_dir=work_dir)

    # 3. Write the artefact and update status.
    blackboard.add_artifact(project_id, "script",
                            {"segments": segments,
                             "n_segments": len(segments)},
                            work_dir=work_dir)
    blackboard.update_status(project_id, "scripted", work_dir=work_dir)
    return segments
```

Three rules every worker follows:

1. **Read the blackboard, don't pass arguments.** If you need research output, read it from `state["artifacts"]["research"]`.
2. **Track every API call's cost.** `blackboard.add_cost(..., usd=...)` so the Router can enforce budget caps next time.
3. **Log errors, don't raise.** Catch exceptions, call `blackboard.log_error(...)`, fall back to a degraded output (silence-stub audio, last-good-frame video, etc.). The pipeline ships.

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
