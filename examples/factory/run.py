#!/usr/bin/env python3
"""End-to-end demo: Router → Blackboard → Voice Synthesizer → ship.

Usage:
  cd examples/factory
  python3 -m factory.run --request "podcast ep019 about EU AI Act"

Env required:
  OPENAI_API_KEY      — Router uses gpt-4o-mini
  ELEVENLABS_API_KEY  — Voice Synth uses ElevenLabs
  ELEVEN_VOICE_ID     — your primary voice id
  ELEVEN_FALLBACK_VOICE_IDS  — comma-separated fallback chain (optional)

What this demo does NOT do:
  - Run a real Research worker (we stub script segments inline below).
  - Run a real Integration worker (no concat, no normalisation, no CDN
    upload). Just leaves the per-segment MP3s on disk.
  - Run a Video Renderer / Visual Director / Thumbnail worker.

That's intentional. This is the SCAFFOLD — the smallest end-to-end shape
that demonstrates the protocol. Drop in real workers per docs/12-factory-floor.md.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Make `from factory import ...` work when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from factory import blackboard, router
from factory.workers import voice_synth


# A stub Script Factory output — what a real Script worker would produce.
# Replace with a call to your script-drafter LLM (see docs/11-storytelling-patterns.md
# for the prompt-engineering side).
DEMO_SEGMENTS = [
    {
        "segment_id": "demo_seg01",
        "type": "intro",
        "text": "Welcome to the Factory Floor demo. This is segment one — short, "
                "deliberately under three seconds so the test runs cheap.",
    },
    {
        "segment_id": "demo_seg02",
        "type": "main",
        "text": "Segment two. The point of this demo is the protocol, not the script.",
    },
]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--request", required=True,
                   help="The user's natural-language request — what the council "
                        "would normally hear in Telegram.")
    p.add_argument("--project-id", default="demo001",
                   help="Slug for this project. Becomes the blackboard filename.")
    p.add_argument("--work-dir", default="",
                   help="Where to put the blackboard JSON + audio outputs. "
                        "Default: ~/.openclaw/factory/")
    p.add_argument("--dry-route", action="store_true",
                   help="Run Router only; don't invoke any worker.")
    args = p.parse_args()

    work_dir = Path(args.work_dir).expanduser() if args.work_dir else None

    # Precondition checks — surface MISSING credentials early, before
    # any LLM calls.
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY missing", file=sys.stderr); return 2

    # 1. Init blackboard
    print(f"[1/3] Init blackboard for project={args.project_id!r}")
    state = blackboard.init(args.project_id, args.request, work_dir=work_dir)
    print(f"  ✓ blackboard at {blackboard._path(args.project_id, work_dir)}")

    # 2. Router classifies + decides
    print(f"\n[2/3] Router decides…")
    decision = router.route(args.project_id, args.request, work_dir=work_dir)
    print(f"  task_type:    {decision['task_type']}")
    print(f"  pipeline:     {decision['pipeline']}")
    print(f"  auto_ship:    {decision['auto_ship']}")
    print(f"  estimated:    ${decision['estimated_cost_usd']:.2f}")
    if decision["blocking_reason"]:
        print(f"  blocked:      {decision['blocking_reason']}")
        print("  → human approval required; not running workers.")
        return 0

    if args.dry_route:
        print("  --dry-route: stopping after Router as requested.")
        return 0

    # 3. Voice Synthesizer worker (the only worker wired up in this demo)
    print(f"\n[3/3] Voice Synthesizer renders {len(DEMO_SEGMENTS)} segments…")
    if not os.environ.get("ELEVENLABS_API_KEY"):
        print("  ! ELEVENLABS_API_KEY missing — cannot run worker. Demo will")
        print("  ! mark all segments as missing and exit successfully (the")
        print("  ! factory pattern: degrade gracefully, never block the chain).")
    primary = os.environ.get("ELEVEN_VOICE_ID", "")
    fallbacks = [v.strip() for v in os.environ.get("ELEVEN_FALLBACK_VOICE_IDS", "").split(",")
                 if v.strip()]
    if not primary:
        print("  ! ELEVEN_VOICE_ID missing — same as above; demo skips synth.")

    if primary and os.environ.get("ELEVENLABS_API_KEY"):
        artifact = voice_synth.synthesize(
            args.project_id, DEMO_SEGMENTS,
            primary_voice_id=primary,
            fallback_voice_ids=fallbacks,
            work_dir=work_dir,
        )
        print(f"  rendered: {artifact['n_rendered']}/{artifact['n_segments']} segments")
        print(f"  voice:    {artifact['voice_used']}")
        if artifact["missing"]:
            print(f"  missing:  {len(artifact['missing'])} segments — see blackboard")

    # Final state read
    final = blackboard.read(args.project_id, work_dir=work_dir)
    print(f"\n=== Final blackboard state ===")
    print(f"  status:       {final['status']}")
    print(f"  cost:         ${final['cost_tracker']['estimated_usd']:.4f}")
    print(f"  api_calls:    {final['cost_tracker']['api_calls']}")
    print(f"  errors:       {len(final['errors'])} logged")
    print(f"\nFull state: {blackboard._path(args.project_id, work_dir)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
