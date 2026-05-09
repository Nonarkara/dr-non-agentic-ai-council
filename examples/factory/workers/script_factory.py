"""Script Factory worker — drafts podcast/video script segments using Dr Non's voice.

Pipeline position: Router → Script Factory → Voice Synth → (Integration).

Critical design points:
- Loads the storytelling brain (openings-bible + techniques) from
  ~/Brain/TemporalLobe/storytelling/ if present. Falls back to a compact
  built-in style block if that path isn't mounted (portable for other users).
- Reads the blackboard for research context and routing decision; adjusts
  segment count and format from that, not from caller arguments.
- Tracks every token + USD for the cost-cap enforcement in the Router.
- On LLM failure: logs error, returns a 2-segment stub so Voice Synth can
  still run and the pipeline ships degraded rather than blocking.

Same discipline as voice_synth.py: stateless function, reads board, does
work, writes artefact back, never raises (logs instead).
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from .. import blackboard

# ---------------------------------------------------------------------------
# Storytelling brain paths
# ---------------------------------------------------------------------------

BRAIN_DIR = Path.home() / "Brain" / "TemporalLobe" / "storytelling"

# Compact fallback when ~/Brain isn't present (portable for other users)
_FALLBACK_STYLE = """\
VOICE RULES (Dr Non Arkara — Harvard PhD, MIT-trained, Bangkok-based):
- Direct, social, declarative. NOT introspective Hollywood-LLM clichés.
- DO NOT open with: "I remember standing/sitting", "Imagine you are",
  "Picture this", "In a world where", "Have you ever", "There's a thing
  I've been thinking about lately".
- Strong openers that work: "People ask me...", a one-sentence vulnerability
  confession, a quote you heard this week + your reaction, or a single
  aphorism/declaration with no setup.
- Short sentences. Paragraph breaks. No padding. Strong verbs.
- Conversational but precise — thinks out loud, not at the reader.
"""


def _load_brain() -> str:
    """Load storytelling reference from ~/Brain. Returns fallback if absent."""
    parts: list[str] = []
    for fname in ("openings-bible.md", "storytelling-techniques.md"):
        p = BRAIN_DIR / fname
        if p.exists():
            try:
                parts.append(p.read_text(encoding="utf-8")[:3500])
            except Exception:
                pass
    return "\n\n---\n\n".join(parts) if parts else _FALLBACK_STYLE


# ---------------------------------------------------------------------------
# System prompt builder
# ---------------------------------------------------------------------------

def _system_prompt(fmt: str) -> str:
    brain = _load_brain()
    return f"""\
You are the Script Factory worker for Dr Non Arkara's media pipeline.

Your job: draft a complete spoken script, broken into segments, for a {fmt}.

--- STORYTELLING BRAIN ---
{brain}
--- END STORYTELLING BRAIN ---

Output JSON ONLY, matching this schema exactly:

{{
  "segments": [
    {{
      "segment_id": "seg01",
      "type": "intro",
      "text": "...",
      "duration_estimate_s": 20
    }}
  ],
  "opening_shape_used": "Shape 1 | Shape 2 | ...",
  "total_duration_estimate_s": 120
}}

Segment rules:
- podcast:      6–10 segments, 600–900 spoken words (~8–10 min)
- wisdom video: 3–5 segments, 150–250 spoken words (~60–90 sec)
- "type" must be one of: "intro" (exactly one), "main", "transition", "outro" (at most one)
- The "intro" segment MUST use one of the 8 shapes from the openings bible
- Record which shape in "opening_shape_used"
- NO markdown in "text" fields — plain spoken words only
- NO commentary, NO markdown wrapper — ONLY valid JSON
"""


# ---------------------------------------------------------------------------
# Stub fallback
# ---------------------------------------------------------------------------

def _write_stub(project_id: str, topic: str,
                work_dir: Path | None) -> list[dict]:
    """Minimal 2-segment stub when the LLM call fails."""
    segs = [
        {
            "segment_id": f"{project_id}_seg01",
            "type": "intro",
            "text": f"Today I want to talk about something that matters: {topic}.",
            "duration_estimate_s": 6,
        },
        {
            "segment_id": f"{project_id}_seg02",
            "type": "main",
            "text": (
                "This is a placeholder — the Script Factory could not draft "
                "the full content. Check the blackboard errors for details."
            ),
            "duration_estimate_s": 10,
        },
    ]
    blackboard.add_artifact(project_id, "script", {
        "segments": segs,
        "opening_shape_used": "stub",
        "total_duration_estimate_s": 16,
        "format": "stub",
        "n_segments": 2,
        "is_stub": True,
    }, work_dir=work_dir)
    blackboard.update_status(project_id, "scripted_stub", work_dir=work_dir)
    return segs


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def draft_script(
    project_id: str,
    topic: str,
    *,
    fmt: str = "auto",              # "podcast" | "video" | "auto"
    openai_api_key: str | None = None,
    work_dir: Path | None = None,
    model: str = "gpt-4o-mini",
    previous_opening_shape: str | None = None,
) -> list[dict]:
    """Draft script segments and write them to the blackboard.

    Args:
        project_id:             Blackboard key for this project.
        topic:                  The subject / user request string.
        fmt:                    "podcast", "video", or "auto" (reads from
                                routing artifact if present).
        openai_api_key:         Falls back to $OPENAI_API_KEY.
        work_dir:               Blackboard directory. Default: ~/.openclaw/factory.
        model:                  OpenAI model. Default: gpt-4o-mini.
        previous_opening_shape: If provided, instruct the LLM to rotate away
                                from this shape (anti-duplicate rule).

    Returns:
        List of segment dicts. On failure, returns a 2-segment stub.
    """
    api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing")

    # Ensure blackboard exists; init if this is the first worker called
    try:
        state = blackboard.read(project_id, work_dir=work_dir)
    except FileNotFoundError:
        blackboard.init(project_id, topic, work_dir=work_dir)
        state = blackboard.read(project_id, work_dir=work_dir)

    blackboard.update_status(project_id, "scripting", work_dir=work_dir)

    # Resolve format from routing artifact if caller said "auto"
    if fmt == "auto":
        pipeline = state.get("artifacts", {}).get(
            "routing", {}).get("pipeline", "video")
        fmt = "podcast" if pipeline == "podcast" else "wisdom video"

    # Pull research notes from board (if a Research worker ran earlier)
    research_ctx = ""
    research = state.get("artifacts", {}).get("research", {})
    notes = research.get("notes", "")
    if notes:
        research_ctx = f"\n\nRESEARCH CONTEXT (use this to ground the script):\n{notes[:2000]}"

    # Opening-shape rotation instruction
    shape_note = ""
    if previous_opening_shape:
        shape_note = (
            f"\n\nIMPORTANT — SHAPE ROTATION: The PREVIOUS piece used "
            f"{previous_opening_shape}. Do NOT use that shape. Pick a different one."
        )

    user_msg = f"TOPIC: {topic}{research_ctx}{shape_note}\n\nDraft the script now."

    # -----------------------------------------------------------------------
    # LLM call
    # -----------------------------------------------------------------------
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": _system_prompt(fmt)},
            {"role": "user",   "content": user_msg},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
        "max_tokens": 2000,
    }).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body, method="POST",
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="replace")[:300]
        except Exception:
            err_body = str(e)
        blackboard.log_error(project_id, "script_factory",
                             f"HTTP {e.code}: {err_body}",
                             action="degrade-stub", work_dir=work_dir)
        return _write_stub(project_id, topic, work_dir)
    except Exception as exc:
        blackboard.log_error(project_id, "script_factory", str(exc)[:300],
                             action="degrade-stub", work_dir=work_dir)
        return _write_stub(project_id, topic, work_dir)

    # Cost tracking — gpt-4o-mini: $0.15/M input, $0.60/M output
    usage = data.get("usage", {})
    in_tok  = usage.get("prompt_tokens", 0)
    out_tok = usage.get("completion_tokens", 0)
    usd = (in_tok * 0.15 / 1_000_000) + (out_tok * 0.60 / 1_000_000)
    blackboard.add_cost(project_id, llm_tokens=in_tok + out_tok,
                        api_call="openai", usd=usd, work_dir=work_dir)

    # -----------------------------------------------------------------------
    # Parse + validate
    # -----------------------------------------------------------------------
    raw = data["choices"][0]["message"]["content"]
    try:
        result  = json.loads(raw)
        segments = result.get("segments", [])
        if not segments:
            raise ValueError("empty segments list")
    except Exception as exc:
        blackboard.log_error(project_id, "script_factory",
                             f"Bad JSON ({exc}): {raw[:200]!r}",
                             action="degrade-stub", work_dir=work_dir)
        return _write_stub(project_id, topic, work_dir)

    # Normalise segment IDs to be project-scoped (model may emit "seg01" etc)
    for i, seg in enumerate(segments, 1):
        sid = seg.get("segment_id", "")
        if not sid or not sid.startswith(project_id):
            seg["segment_id"] = f"{project_id}_seg{i:02d}"

    artifact = {
        "segments":                 segments,
        "opening_shape_used":       result.get("opening_shape_used", "unknown"),
        "total_duration_estimate_s": result.get("total_duration_estimate_s", 0),
        "format":                   fmt,
        "n_segments":               len(segments),
    }
    blackboard.add_artifact(project_id, "script", artifact, work_dir=work_dir)
    blackboard.update_status(project_id, "scripted", work_dir=work_dir)
    return segments
