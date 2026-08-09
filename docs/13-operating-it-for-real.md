# 13 — Operating It For Real

> Everything above this document describes how the council is *built*.
> This one is about what happened when it had to run unattended for a summer.
>
> Every item below is a real incident with a real root cause. None of them were
> found by reading code. All of them were found by something going quietly
> wrong for days.

The theme, if there is one: **the failure is almost never where the alarm is
pointing.** A podcast pipeline broke because a disk was full. A voice service
died because a health check was too healthy. A bot went silent because a cable
was loose. If you take one thing from this page, take the habit of asking
"what would make this symptom a *lie*?"

---

## 1. A fallback chain made entirely of free tiers is not a fallback chain

**Symptom:** 24 consecutive nightly renders produced nothing. The morning push
sent a bare header with no content — which reads to a user as "the bot is
dead", not "generation failed".

**Cause:** the model chain was three *free remote* routes. Free tiers are
routinely all-rate-limited at the same time of night. Three of them is not
redundancy; it is one point of failure wearing three hats.

**Fix:** add a local last resort. A plain briefing written by a 4B model on
your own machine beats no briefing.

```
primary (free) → alternate (free) → auto (free) → LOCAL MODEL
```

**Generalise:** redundancy only counts if the failure modes are *independent*.
Count your independent failure modes, not your providers.

---

## 2. Thinking models return empty strings

**Symptom:** the local fallback ran, exited 0, and produced an empty script.

**Cause:** reasoning models spend the `num_predict` budget on hidden thinking
tokens and return an empty visible `content` field. Nothing errors. You get a
successful call with nothing in it.

**Fix:** disable thinking explicitly for generation tasks, and salvage the
reasoning field rather than failing on empty:

```jsonc
{ "model": "...", "think": false, "options": { "num_predict": 4000 } }
```

**The part that matters:** the short unit test passed. It only reproduced with
a real, full-size prompt. A test with unrealistic inputs will hide this class
of bug perfectly.

---

## 3. Context windows truncate silently

A local runtime defaulted to roughly a 4k context. The real prompt was 40k+
characters of source material. It did not error, it did not warn — it silently
dropped most of the input and produced a confident, thin answer.

Set the window explicitly (`num_ctx`), and when you have to shrink it, **shrink
the input yourself** rather than letting the server truncate. Server-side
truncation cuts from wherever it likes — which in one case removed the closing
output-format instructions, so the model returned unusable prose instead of the
required structure.

---

## 4. Local models narrate their homework

Small models often open with their planning: *"Okay, the user wants me to write
a script. Let me unpack this..."* — which a text-to-speech stage will happily
read aloud as the first line of your episode.

The first fix attempted phrase-matching against a list of known meta-phrases.
**It failed in production** on a bullet-list preamble that matched no phrase.

The fix that held was **structural**: the output format requires every spoken
line to carry a speaker label, so find the first label and discard everything
before it, regardless of wording.

> Prefer structural invariants over blocklists. A blocklist is a bet that you
> imagined every variation. Structure is a property of the format itself.

---

## 5. Health checks that answer instantly are health checks that lie

**Symptom:** a monitor logged `OK: model server alive` every five minutes,
straight through a total outage.

**Cause:** the probe hit `/api/version`. That endpoint answers in milliseconds
whether or not inference works. Meanwhile the actual inference path was wedged
— zero bytes returned, ever.

**Rule:** *a probe must exercise the same code path that fails.* If the thing
that breaks is inference, the probe must run inference.

---

## 6. …and then the honest probe caused the outage

This one is worth internalising because the fix created the next incident.

The corrected probe ran a real inference call. Real inference **loads the
model** — roughly 3GB — and the runtime pins it in memory for its default
keep-alive of five minutes. A probe on a five-minute schedule therefore keeps
a 3GB model resident permanently.

On a 16GB machine, that was enough to starve the *text-to-speech service the
monitor existed to protect*. Two model workers were found resident, held by
nothing but health checks, while the protected service sat swapped out and
unresponsive.

**Fix:** `"keep_alive": 0` — verify the path, then release immediately.

> A health check is not free. If it reserves a resource, it is part of the
> system it is measuring.

---

## 7. Restarts that silently do nothing, 198 times

**Symptom:** a monitor reported a service down and "restarting" every five
minutes for an entire day — 198 restarts, 30 push notifications, no recovery.

**Two independent bugs:**

1. **`open -a AppName` is a no-op when the app is already running.** The kill
   list only contained the *server child* process. So the child died, the
   parent survived, nothing respawned, and the "restart" did nothing at all —
   silently, forever. Kill patterns must include the **parent** process.

2. **The restart throttle keyed off process age.** When a service fails to
   spawn *at all*, there is no process, so there is no age, so the throttle is
   skipped entirely and it retries every cycle. Throttle on **last restart
   time**, recorded in state — that covers the no-process case.

```python
last = state.get("last_restart", {}).get(name)
if last and (now - last) < GRACE:
    return                      # still inside the grace window
state.setdefault("last_restart", {})[name] = now
```

---

## 8. Alert fatigue is a system failure, not a user failure

Thirty identical "SERVICE DOWN" messages in one day for one already-known
fault is how a person learns to swipe your alerts away without reading them —
and then misses the one that mattered.

Exponential backoff while a fault **persists**, reset on recovery:

```
30m → 1h → 2h → 4h → 6h (cap)
```

Simulated across 24h of continuous downtime, that is **7 alerts instead of 30**,
while a genuinely new incident still pages immediately.

---

## 9. Never put a live dependency behind removable media

This happened **three separate times** with three different drives before the
lesson took.

The failure never announces itself as "the drive is gone". It presents as:

- a bot going dormant while its gateway still reports healthy
- a voice service that loads to 0.3GB, stalls at 0% CPU, and never answers
- a service that cannot start because its *working directory* is a symlink to
  the missing volume

**Diagnostic that settles it in one command** — if raw device reads fail, it is
hardware or bus, and no amount of filesystem or config work will help:

```bash
dd if=/dev/rdiskN of=/dev/null bs=1m count=1
```

**Also:** unmounting a wedged volume means fighting a chain of dissenting
processes (every service with data on it). `diskutil unmount force` is the
standard escape hatch on journaled filesystems that are already failing I/O.

---

## 10. A full disk breaks your local models

The single most surprising root cause of the summer.

**Symptom:** local generation failed instantly with
`Remote end closed connection without response`. A 1-token probe always
succeeded. Every model-side theory (context size, quantisation, model choice)
was wrong.

**Cause:** swap lives on the boot volume. The disk was at 1.4GB free. When the
runtime tried to allocate a multi-GB KV cache, the kernel needed to grow swap,
swap could not grow, and the worker died — surfacing as a dropped connection.
The tiny probe never failed because it never needed a big allocation.

Freeing disk fixed "the model problem" with no model changes at all.

> `Remote end closed connection` from a local inference server is an
> **allocation** failure. Check `df -h /` and swap usage *before* touching
> model parameters.

**Where the disk actually went** (also not where anyone looked): daily database
snapshots with retention counts set years ago against databases that had since
grown to multiple GB — 14 snapshots × 2.2GB is 30GB of "backups" nobody
budgeted for. And on a copy-on-write filesystem, `df` reports *container* free
space shared across volumes; per-volume tools tell the truth.

---

## 11. Small operational landmines that cost real hours

| Landmine | What actually happens |
|---|---|
| `pkill -f "a\|b"` | macOS `pkill` has no BRE alternation — it silently matches **nothing**, so your "restart" never kills anything |
| Config fixed, still broken | A long-lived process is still holding the *old* config in memory. A config fix isn't a fix until every process that read it has restarted |
| Hard-coded model names | Providers retire models. One returned HTTP 400 for weeks. Verify against `GET /v1/models` before trusting any name in config |
| Endpoint capability mismatch | A vision call failed with `content.type` illegal, allowed `['text']`. The base URL pointed at a **coding** endpoint (text-only) — and that plan had no vision model at all. List the models; don't assume the family has the capability |
| Charset labels | One email labelled `windows-874` (Python only knows `cp874`) raised out of the **entire** fetch loop, silently halving the input from 30 items to 15, with one stderr line as the only trace |
| `exec` kills your cleanup | `exec caffeinate ...` replaces the shell, so the `EXIT` trap never runs and the lock file leaks forever |
| Scheduler catch-up | Interval-based schedulers fire missed runs after sleep/wake. Idempotent jobs make this a non-event; non-idempotent ones double-process |

---

## 12. Make long jobs resumable, then retrying is free

The change that did more for reliability than any other single fix.

A nightly job that ingests, generates, then renders audio for two hours is a
long chain where any link can break. Originally a failure anywhere threw away
everything.

Two guards make the whole thing safely retryable:

- **Already-done check** — if the final artefact exists, exit immediately.
- **Resume check** — if the *expensive intermediate* (the script) exists, skip
  ingestion and generation entirely and go straight to rendering.

With those in place, a retry ladder becomes safe and cheap:

```
21:00  full attempt
23:30  retry — resumes from whatever succeeded
02:00  retry
04:30  last chance before delivery
```

Each rung only redoes the part that actually failed. A transient rate-limit at
21:00 stops being a missed morning.

**Add a lock.** Two concurrent runs of a memory-hungry job on one machine is
the same resource exhaustion that breaks everything else here. `mkdir` is
atomic and works fine as a lock — with a stale-lock check for the case where a
previous run was killed before its cleanup ran.

---

## 13. The meta-lesson: verify empirically, at real scale

Nearly every bug on this page shares a shape: **something reported success
while doing nothing useful.** Empty strings from successful calls. Health
checks passing on dead services. Restarts that restart nothing. Truncation
with no warning. Imports that silently skip everything.

Three habits that catch this class:

1. **Test against real inputs at real size.** The short test passes. The 40k
   prompt does not.
2. **Verify the effect, not the exit code.** After an import, count the rows.
   After a restart, check the PID changed. After a "fix", reproduce the
   original failure and watch it not happen.
3. **When you write a defensive fix, deliberately trigger the thing it defends
   against.** One race-condition guard here had a one-character path bug that
   made it a permanent no-op. It compiled, it ran nightly, it did nothing —
   and it was only caught by constructing the exact failure it existed to
   catch. That test then recovered 37 real messages that had been silently
   dropping.

---

## The short version

- Redundancy across providers that share a failure mode is not redundancy
- A probe must exercise the path that breaks — and must not reserve what it measures
- Alerts that repeat are alerts that get ignored
- Live dependencies never go behind removable media
- `Remote end closed connection` locally means *allocation*, so check the disk
- Make expensive steps resumable and retries become free
- A fix is not a fix until you have watched the original failure fail to happen
