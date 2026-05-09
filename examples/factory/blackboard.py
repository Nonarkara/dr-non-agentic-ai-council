"""Blackboard — the shared JSON state store every factory worker reads + writes.

Stateless workers, stateful board. No conversation history passed between
workers — they communicate only by reading and writing this file.

For prototyping: a single JSON file on disk per project_id.
For scale: swap _read/_write for Redis, or any KV store. The interface
stays the same.

Schema (every project_id state):

    {
      "project_id": "ep019",
      "status": "init|researching|scripting|voicing|rendering|shipped|failed",
      "auto_ship": true,
      "created_at": "2026-05-09T14:05:00Z",
      "request": "<original user request text>",
      "artifacts": {
        "research": {...},
        "script": {"segments": [...], "completed_at": "..."},
        "audio": {"files": [...], "completed_at": "..."},
        "video": {"scenes": [...], "status": "pending"},
        "final": {"url": null}
      },
      "errors": [
        {"agent": "voice_synth", "time": "...", "error": "...", "action": "retry_2_of_3"}
      ],
      "cost_tracker": {
        "llm_tokens": 0,
        "api_calls": {"elevenlabs": 0, "openai": 0},
        "estimated_usd": 0.0
      }
    }

Atomic writes: we write to <file>.tmp and os.replace() — survives crashes
mid-write without leaving partial JSON.
"""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

DEFAULT_DIR = Path.home() / ".openclaw" / "factory"


def _path(project_id: str, work_dir: Path | None = None) -> Path:
    return (work_dir or DEFAULT_DIR) / f"{project_id}.json"


def init(project_id: str, request: str, *, auto_ship: bool = True,
         work_dir: Path | None = None) -> dict:
    """Create a fresh blackboard for a new project. Returns the state dict."""
    work_dir = work_dir or DEFAULT_DIR
    work_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "project_id": project_id,
        "status": "init",
        "auto_ship": auto_ship,
        "created_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "request": request,
        "artifacts": {},
        "errors": [],
        "cost_tracker": {"llm_tokens": 0, "api_calls": {}, "estimated_usd": 0.0},
    }
    write(state, work_dir=work_dir)
    return state


def read(project_id: str, *, work_dir: Path | None = None) -> dict:
    p = _path(project_id, work_dir)
    if not p.exists():
        raise FileNotFoundError(f"no blackboard for project {project_id!r}")
    return json.loads(p.read_text())


def write(state: dict, *, work_dir: Path | None = None) -> None:
    """Atomic write — survives crash mid-write."""
    work_dir = work_dir or DEFAULT_DIR
    work_dir.mkdir(parents=True, exist_ok=True)
    p = _path(state["project_id"], work_dir)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, default=str))
    os.replace(tmp, p)


def update_status(project_id: str, status: str, *,
                  work_dir: Path | None = None) -> dict:
    """Worker calls this when it transitions phase."""
    state = read(project_id, work_dir=work_dir)
    state["status"] = status
    write(state, work_dir=work_dir)
    return state


def add_artifact(project_id: str, key: str, value: dict, *,
                 work_dir: Path | None = None) -> dict:
    """Worker writes its output here. Key is e.g. 'script', 'audio', 'video'."""
    state = read(project_id, work_dir=work_dir)
    value = {**value, "completed_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"}
    state["artifacts"][key] = value
    write(state, work_dir=work_dir)
    return state


def log_error(project_id: str, agent: str, error: str, action: str = "logged",
              *, work_dir: Path | None = None) -> dict:
    """Worker logs a failure (or a retry attempt) for post-hoc QA."""
    state = read(project_id, work_dir=work_dir)
    state["errors"].append({
        "agent": agent,
        "time": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "error": error[:500],   # cap to keep blackboard small
        "action": action,
    })
    write(state, work_dir=work_dir)
    return state


def add_cost(project_id: str, *, llm_tokens: int = 0, api_call: str | None = None,
             usd: float = 0.0, work_dir: Path | None = None) -> dict:
    """Track running spend so the Router can enforce budget caps."""
    state = read(project_id, work_dir=work_dir)
    ct = state["cost_tracker"]
    ct["llm_tokens"] = ct.get("llm_tokens", 0) + llm_tokens
    if api_call:
        ct["api_calls"][api_call] = ct["api_calls"].get(api_call, 0) + 1
    ct["estimated_usd"] = round(ct.get("estimated_usd", 0.0) + usd, 4)
    write(state, work_dir=work_dir)
    return state
