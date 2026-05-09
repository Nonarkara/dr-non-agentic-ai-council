"""Router — the traffic cop. Lightweight LLM classifier, binary GO / BLOCK.

Zero creativity. Zero deliberation. Reads the user request, classifies the
task type, picks a pipeline, and writes its decision to the blackboard.

Why a separate Router (vs. just deciding inline in run.py)? Two reasons:
  1. Router decisions are auditable in the blackboard's `routing` artifact.
     If the wrong pipeline ran, you can re-prompt the Router with a tweak.
  2. Router can refuse (auto_ship=false) on budget / new-voice / flagged
     keywords without invoking any expensive worker.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from . import blackboard

ROUTER_SYSTEM_PROMPT = """\
You are the Factory Floor's Router agent. Your only job is to classify
an incoming user request and decide whether it can auto-ship.

Output JSON ONLY, matching this schema exactly:

{
  "task_type": "podcast" | "video" | "blog" | "research" | "mixed",
  "pipeline":  "podcast" | "video" | "blog" | "research",
  "auto_ship": true | false,
  "required_workers": ["research", "script", "voice", "integration"],
  "estimated_cost_usd": 0.00,
  "blocking_reason": null
}

Rules:
- auto_ship = false ONLY if any of:
  * the request mentions a NEW voice clone the system hasn't used before
  * the topic is potentially controversial (politics, named individuals,
    legal advice, medical advice)
  * the estimated cost exceeds $5
  * the request is ambiguous (you'd need to ask a clarifying question)
- Otherwise auto_ship = true.
- estimated_cost_usd is your best guess based on length / pipeline.
  Podcast: ~$0.50 for 10 min. Video: ~$0.25 for 60 sec. Blog: ~$0.01.
- required_workers is the SUBSET needed for THIS request, not all.
- blocking_reason is a single sentence ONLY if auto_ship=false; else null.
- NO commentary. NO markdown. JUST the JSON.
"""


def route(project_id: str, request: str, *,
          openai_api_key: str | None = None,
          work_dir: Path | None = None,
          model: str = "gpt-4o-mini") -> dict:
    """Run the Router for one project. Writes decision to blackboard.

    Returns the routing decision dict.
    """
    api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing")

    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": f"REQUEST:\n{request}"},
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
        "max_tokens": 300,
    }).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body, method="POST",
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        # On Router failure, default-deny: don't auto-ship if we can't
        # even classify. That's safer than running unrestricted.
        decision = {
            "task_type": "unknown",
            "pipeline": "none",
            "auto_ship": False,
            "required_workers": [],
            "estimated_cost_usd": 0.0,
            "blocking_reason": f"Router unreachable: HTTP {e.code}",
        }
        blackboard.log_error(project_id, "router",
                             f"Router HTTP {e.code}: {e.read()[:200]!r}",
                             action="default-deny",
                             work_dir=work_dir)
        blackboard.add_artifact(project_id, "routing", decision, work_dir=work_dir)
        return decision

    raw = data["choices"][0]["message"]["content"]
    decision = json.loads(raw)

    # Track cost — gpt-4o-mini at $0.15/M input + $0.60/M output
    usage = data.get("usage", {})
    in_tok = usage.get("prompt_tokens", 0)
    out_tok = usage.get("completion_tokens", 0)
    usd = (in_tok * 0.15 / 1_000_000) + (out_tok * 0.60 / 1_000_000)
    blackboard.add_cost(project_id, llm_tokens=in_tok + out_tok,
                        api_call="openai", usd=usd, work_dir=work_dir)

    # Hard budget cap: even if Router said auto_ship=true, refuse if
    # cumulative cost is already past $20. (Defensive — usually only
    # matters in long-running multi-pipeline jobs.)
    state = blackboard.read(project_id, work_dir=work_dir)
    if state["cost_tracker"]["estimated_usd"] > 20.0:
        decision["auto_ship"] = False
        decision["blocking_reason"] = "hard budget cap of $20 hit"

    blackboard.add_artifact(project_id, "routing", decision, work_dir=work_dir)
    blackboard.update_status(project_id,
                             "blocked" if not decision["auto_ship"] else "routed",
                             work_dir=work_dir)
    return decision
