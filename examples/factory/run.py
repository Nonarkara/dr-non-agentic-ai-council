#!/usr/bin/env python3
"""End-to-end demo: Router → Script Factory → Voice Synthesizer → ship.

Usage:
  cd examples/
  python3 -m factory.run --request "podcast ep019 about EU AI Act"

Env required:
  OPENAI_API_KEY      — Router + Script Factory use gpt-4o-mini
  ELEVENLABS_API_KEY  — Voice Synth uses ElevenLabs
  ELEVEN_VOICE_ID     — your primary voice id
  ELEVEN_FALLBACK_VOICE_IDS  — comma-separated fallback chain (optional)

Flags:
  --dry-route     Router only (no LLM script, no audio)
  --dry-script    Router + Script Factory (no audio spend)

What this demo does NOT do:
  - Run a real Research worker (no Perplexity / search calls).
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
from factory.workers import script_factory, voice_synth


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
    p.add_argument("--dry-script", action="store_true",
                   help="Run Router + Script Factory but skip Voice Synth "
                        "(useful for checking the script without spending ElevenLabs quota).")
    args = p.parse_args()

    work_dir = Path(args.work_dir).expanduser() if args.work_dir else None

    # Precondition checks — surface missing credentials early.
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY missing", file=sys.stderr)
        return 2

    # ------------------------------------------------------------------
    # 1. Init blackboard
    # ------------------------------------------------------------------
    print(f"[1/4] Init blackboard for project={args.project_id!r}")
    blackboard.init(args.project_id, args.request, work_dir=work_dir)
    print(f"  ✓ blackboard at {blackboard._path(args.project_id, work_dir)}")

    # ------------------------------------------------------------------
    # 2. Router classifies + decides
    # ------------------------------------------------------------------
    print(f"\n[2/4] Router decides…")
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
        _print_final(args.project_id, work_dir)
        return 0

    # ------------------------------------------------------------------
    # 3. Script Factory drafts the script
    # ------------------------------------------------------------------
    print(f"\n[3/4] Script Factory drafts script…")
    segments = script_factory.draft_script(
        args.project_id,
        args.request,
        work_dir=work_dir,
    )
    state = blackboard.read(args.project_id, work_dir=work_dir)
    script_art = state.get("artifacts", {}).get("script", {})
    is_stub = script_art.get("is_stub", False)
    n_segs = script_art.get("n_segments", len(segments))
    total_s = script_art.get("total_duration_estimate_s", 0)
    opening = script_art.get("opening_shape_used", "unknown")

    print(f"  segments:     {n_segs}")
    print(f"  duration est: ~{total_s}s")
    print(f"  opening:      {opening}")
    if is_stub:
        print(f"  ⚠ stub script — LLM call failed; see blackboard errors")

    if args.dry_script:
        print("  --dry-script: stopping before Voice Synth as requested.")
        print()
        print("  Script preview:")
        for seg in segments:
            print(f"    [{seg['type']}] {seg['text'][:80]}…"
                  if len(seg['text']) > 80 else f"    [{seg['type']}] {seg['text']}")
        _print_final(args.project_id, work_dir)
        return 0

    # ------------------------------------------------------------------
    # 4. Voice Synthesizer renders the segments
    # ------------------------------------------------------------------
    print(f"\n[4/4] Voice Synthesizer renders {len(segments)} segments…")
    if not os.environ.get("ELEVENLABS_API_KEY"):
        print("  ! ELEVENLABS_API_KEY missing — skipping Voice Synth.")
        print("  ! (factory pattern: degrade gracefully, never block)")
        _print_final(args.project_id, work_dir)
        return 0

    primary = os.environ.get("ELEVEN_VOICE_ID", "")
    if not primary:
        print("  ! ELEVEN_VOICE_ID missing — skipping Voice Synth.")
        _print_final(args.project_id, work_dir)
        return 0

    fallbacks = [v.strip() for v in
                 os.environ.get("ELEVEN_FALLBACK_VOICE_IDS", "").split(",")
                 if v.strip()]

    artifact = voice_synth.synthesize(
        args.project_id, segments,
        primary_voice_id=primary,
        fallback_voice_ids=fallbacks,
        work_dir=work_dir,
    )
    print(f"  rendered: {artifact['n_rendered']}/{artifact['n_segments']} segments")
    print(f"  voice:    {artifact['voice_used']}")
    if artifact["missing"]:
        print(f"  missing:  {len(artifact['missing'])} segments — see blackboard")

    _print_final(args.project_id, work_dir)
    return 0


def _print_final(project_id: str, work_dir: Path | None) -> None:
    final = blackboard.read(project_id, work_dir=work_dir)
    print(f"\n=== Final blackboard state ===")
    print(f"  status:       {final['status']}")
    print(f"  cost:         ${final['cost_tracker']['estimated_usd']:.4f}")
    print(f"  api_calls:    {final['cost_tracker']['api_calls']}")
    print(f"  errors:       {len(final['errors'])} logged")
    print(f"\nFull state: {blackboard._path(project_id, work_dir)}")


if __name__ == "__main__":
    sys.exit(main())
