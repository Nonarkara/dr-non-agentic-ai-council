"""Voice Synthesizer worker — direct ElevenLabs API caller.

Critical design point: this worker has DIRECT API CREDENTIALS. It doesn't
ask another agent to call ElevenLabs for it. It doesn't post a delegation
message to the chat. It calls the HTTP endpoint itself, retries with
backoff, and falls back to a base voice if the cloned voice fails.

That's the whole shift from council to factory. The worker has the
key + the FFmpeg + the API client. No proxy. No approval gate.

Circuit-breaker behaviour:
  Retry 1 (rate limit / transient):  wait 2s, retry primary voice
  Retry 2:                           wait 5s, retry primary voice
  Retry 3 (or `voice_not_fine_tuned`): swap to fallback voice
  All-fail:                          log to blackboard, mark segment
                                     as missing, ship rest of pipeline.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from .. import blackboard


def _eleven_post(api_key: str, voice_id: str, text: str,
                 out_path: Path, *, timeout: int = 180) -> tuple[bool, str]:
    """One ElevenLabs POST. Returns (ok, error_string)."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    body = json.dumps({
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"xi-api-key": api_key,
                 "Content-Type": "application/json",
                 "Accept": "audio/mpeg"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            audio = r.read()
        if len(audio) < 1024:
            return False, f"response too small ({len(audio)} bytes)"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(audio)
        return True, ""
    except urllib.error.HTTPError as e:
        try:
            err = e.read().decode("utf-8", errors="replace")
        except Exception:
            err = str(e)
        return False, f"HTTP {e.code}: {err[:300]}"
    except Exception as e:
        return False, str(e)[:300]


def synthesize(project_id: str, segments: list[dict], *,
               primary_voice_id: str,
               fallback_voice_ids: list[str] | None = None,
               api_key: str | None = None,
               work_dir: Path | None = None,
               out_dir: Path | None = None,
               max_retries: int = 3,
               backoff: tuple[int, ...] = (2, 5, 15)) -> dict:
    """Render every script segment to MP3 with retry+fallback discipline.

    `segments` is a list like [{"segment_id": "ep019_seg01", "text": "..."}].

    Returns an artifact dict suitable for blackboard.add_artifact("audio", ...):
        {
          "files": [{"segment_id": "...", "path": "..."}],
          "missing": [{"segment_id": "...", "reason": "..."}],
          "voice_used": "primary|fallback:<id>"
        }
    """
    api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY missing")

    work_dir = work_dir or blackboard.DEFAULT_DIR
    out_dir = out_dir or (work_dir / project_id / "audio")
    out_dir.mkdir(parents=True, exist_ok=True)

    fallback_voice_ids = list(fallback_voice_ids or [])
    blackboard.update_status(project_id, "voicing", work_dir=work_dir)

    files: list[dict] = []
    missing: list[dict] = []
    voice_used = "primary"

    for seg in segments:
        seg_id = seg["segment_id"]
        text = seg["text"]
        out_path = out_dir / f"{seg_id}.mp3"
        chain = [primary_voice_id] + [v for v in fallback_voice_ids
                                       if v != primary_voice_id]

        rendered = False
        for attempt in range(max_retries):
            voice_id = chain[min(attempt, len(chain) - 1)]
            ok, err = _eleven_post(api_key, voice_id, text, out_path)

            # Track every API call for cost accounting. ElevenLabs ~$0.30/min,
            # ~150 chars/min spoken; rough usd per char = 0.30 / (150 * 60) ≈ $3.3e-5
            est_usd = len(text) * 3.3e-5
            blackboard.add_cost(project_id, api_call="elevenlabs", usd=est_usd,
                                 work_dir=work_dir)

            if ok:
                files.append({"segment_id": seg_id, "path": str(out_path),
                              "voice_id_used": voice_id})
                if voice_id != primary_voice_id:
                    voice_used = f"fallback:{voice_id}"
                rendered = True
                break

            # Decide retry vs immediate fallback based on error class
            is_voice_not_finetuned = (
                "not fine-tuned" in err or "voice_not_fine_tuned" in err)
            is_rate_limit = "429" in err or "rate" in err.lower()

            blackboard.log_error(
                project_id, "voice_synth",
                f"seg={seg_id} voice={voice_id[:8]} attempt={attempt+1}: {err}",
                action=("fallback-voice" if is_voice_not_finetuned
                        else f"retry_{attempt+2}_of_{max_retries}"),
                work_dir=work_dir,
            )

            if is_voice_not_finetuned:
                # Skip ahead — primary voice will keep failing. Force fallback.
                continue
            if is_rate_limit and attempt < max_retries - 1:
                time.sleep(backoff[min(attempt, len(backoff) - 1)])
                continue
            if attempt < max_retries - 1:
                time.sleep(backoff[min(attempt, len(backoff) - 1)])
                continue
            # Last attempt; loop will exit

        if not rendered:
            # Degrade gracefully — log the missing segment, continue with rest.
            # The Integration worker will leave a silence-gap or a TTS-stub
            # in its place rather than block the whole pipeline.
            missing.append({"segment_id": seg_id,
                            "reason": "all retries + fallback voices exhausted"})

    artifact = {
        "files": files,
        "missing": missing,
        "voice_used": voice_used,
        "n_segments": len(segments),
        "n_rendered": len(files),
    }
    blackboard.add_artifact(project_id, "audio", artifact, work_dir=work_dir)

    # Status: shipped-with-warnings vs failed. The factory ships even when
    # some segments are missing (graceful degradation); only true zero-output
    # counts as failed.
    if not files:
        blackboard.update_status(project_id, "failed", work_dir=work_dir)
    elif missing:
        blackboard.update_status(project_id, "voiced_with_warnings",
                                 work_dir=work_dir)
    else:
        blackboard.update_status(project_id, "voiced", work_dir=work_dir)

    return artifact
