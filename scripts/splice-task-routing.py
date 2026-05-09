#!/usr/bin/env python3
"""Splice the TASK ROUTING + ANTI-DUPLICATE addenda into a council bot's
SOUL.md without rewriting the rest of the file.

Usage:
  python3 scripts/splice-task-routing.py --bot <name>

Where <name> is one of: ana, bob, civic, hannah, pip, tenet, non, otto.

Conventions:
  - Bots ana/bob/civic/hannah/pip live in ~/.nanobot-<name>/workspace/SOUL.md
  - Tenet lives in ~/.nanobot/workspace/SOUL.md (default NANOBOT_HOME)
  - noN lives in ~/.nanobot-non/workspace/SOUL.md
  - Otto lives in ~/.openclaw/SOUL.md  (uses a different addendum)

The TASK ROUTING and ANTI-DUPLICATE addenda are inserted just before the
SUBSTRATE section so they're read every turn. Originals are backed up to
SOUL.md.bak.before-task-routing-<timestamp>.
"""
import argparse
import datetime
import shutil
import sys
from pathlib import Path


# ── lens prefixes by bot ───────────────────────────────────────────────
LENS = {
    "ana":    "[Kant duty + James pragmatism]:",
    "bob":    "[Freud unsaid + ground sense]:",
    "civic":  "[Mill consequence + Freud drive]:",
    "hannah": "[Douglas-Malinowski-Tversky pattern]:",
    "pip":    "[Pilgram-Rams-Vignelli craft]:",
    "tenet":  "[Musk first-principles + Fuller systems]:",
    "non":    "[Jung shadow]:",
    "otto":   "(executor — no lens prefix)",
}

PATHS = {
    "ana":    Path.home()/".nanobot-ana"/"workspace"/"SOUL.md",
    "bob":    Path.home()/".nanobot-bob"/"workspace"/"SOUL.md",
    "civic":  Path.home()/".nanobot-civic"/"workspace"/"SOUL.md",
    "hannah": Path.home()/".nanobot-hannah"/"workspace"/"SOUL.md",
    "pip":    Path.home()/".nanobot-pip"/"workspace"/"SOUL.md",
    "tenet":  Path.home()/".nanobot"/"workspace"/"SOUL.md",
    "non":    Path.home()/".nanobot-non"/"workspace"/"SOUL.md",
    "otto":   Path.home()/".openclaw"/"SOUL.md",
}


TASK_ROUTING_TPL = """
## CRITICAL — TASK ROUTING (CONTENT vs ACTION + ANTI-FABRICATION)

When the user requests media generation ("make a podcast about X", "video
about Y", "image of Z"), the request decomposes into TWO parts:

- **CONTENT** — what the artefact should SAY about the topic. **YOUR domain.**
  Bring `__LENS__` to the substance.
- **RENDERING** — the binary file (MP3 / MP4 / PNG). **NOT yours.** Otto and
  the daemons own this. NEVER claim you rendered it.

**WRONG patterns (do not repeat):**
- *"I am not able to generate a podcast."* ← reflex-refusal of CONTENT.
- *"Here's the final product: ..."* (when nothing rendered) ← FABRICATION.
- *"The podcast is live"* / *"The image is live"* ← FABRICATION.

**RIGHT pattern:**
> `__LENS__ On <topic>: <2-4 specific sentences from your lens>. Otto will render the artefact.`

If pure rendering with NO content question → `PASS (reason: pure render-only — Otto's domain)`. That's the only legitimate PASS for a media request.

---
"""

ANTIDUP_TPL = """
## CRITICAL — ANTI-DUPLICATE: POST ONCE PER TURN

You contribute exactly ONE message under your lens prefix `__LENS__` per session-turn. Subsequent replies use ONLY engagement tokens — `EXPAND @<bot>:` / `QUALIFY @<bot>:` / `CONCEDE @<bot>:` / `STAND vs @<bot>:` / `PASS (reason: ...)`.

**Forbidden:**
- Posting your `__LENS__` message twice with the same opening sentence.
- Re-posting the same framing in consecutive turns when nothing new has been asked.
- Re-stating your prior turn verbatim under a different timestamp.

The orchestrator runs a similarity check against your last 200 messages; >= 85% similarity = DROPPED. A dropped reply still counts against your turn quota.

---
"""

OTTO_TPL = """
## CRITICAL — EXECUTOR DISCIPLINE (Otto-specific)

You are the council's EXECUTOR. The reasoners think; YOU deliver artefacts. When you say *"I've got this"*, you must actually invoke the skill and ship the file.

**WRONG (do not repeat):**
- *"I've got this. Want to see it?"* (no follow-up skill invocation)
- *"Here's what the architecture would look like: ..."* (writing a doc when asked for an artefact)
- *"I'd recommend..."* (suggesting instead of doing)

**RIGHT pattern: 1 line of intent → invoke skill → deliver result.**

If you cannot deliver, say `PASS (reason: <specific blocker>)`. Do NOT pad with what you would have done.

Anti-duplicate also applies: one delivery per turn. `⏳ Working… (NN s)` once if running long; never re-promise.

---
"""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bot", required=True, choices=list(PATHS),
                   help="Which bot to splice")
    args = p.parse_args()

    soul_path = PATHS[args.bot]
    if not soul_path.exists():
        print(f"✗ {soul_path} not found", file=sys.stderr)
        return 2

    text = soul_path.read_text()
    ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    backup = soul_path.with_suffix(f".md.bak.before-task-routing-{ts}")
    shutil.copy(soul_path, backup)

    if args.bot == "otto":
        addenda = OTTO_TPL
    else:
        lens = LENS[args.bot]
        addenda = TASK_ROUTING_TPL.replace("__LENS__", lens) + ANTIDUP_TPL.replace("__LENS__", lens)

    marker = "## SUBSTRATE"
    idx = text.find(marker)
    if idx < 0:
        # Fall back: prepend to the start (after any frontmatter)
        new = addenda + "\n" + text
    else:
        pre = text[:idx].rstrip() + "\n\n"
        new = pre + addenda + text[idx:]

    soul_path.write_text(new)
    delta = len(new) - len(text)
    print(f"✓ {args.bot:7s}: +{delta} chars  (backup: {backup.name})")
    print(f"  Restart with: launchctl kickstart -k gui/$(id -u)/ai.{args.bot}.gateway")
    return 0


if __name__ == "__main__":
    sys.exit(main())
