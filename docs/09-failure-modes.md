# 09 — Failure modes (what goes wrong, what to do)

> Real failures from the live council, and how to fix them.

## Bot stops responding

### Symptom

You message the group chat. Most bots reply, one stays silent.

### Likely causes (in order of probability)

1. **Provider rate limit hit.** That bot's provider returned 429 for the whole turn.
2. **Provider monthly cap exhausted.** NVIDIA NIM gives 1000 req/month/model — easy to hit if the bot is on a heavily-used model.
3. **Provider transient outage** (Cloudflare incident, regional Google issue, AliCloud international endpoint hiccup).
4. **Bot gateway crashed.** launchd will auto-restart, but there's a 10-30 sec window where it's silent.
5. **Telegram API rate-limited the bot's polling** (unusual; happens after many bots in the same group).

### Diagnosis

```bash
# 1. Check if the gateway is running
launchctl print gui/$(id -u)/ai.<bot>.gateway 2>&1 | grep "pid ="

# 2. Tail the gateway log for errors
tail -50 ~/.nanobot-<bot>/logs/gateway.log | grep -E "error|429|403|401|timeout|exception"

# 3. Check the provider directly via curl
# Example for Groq:
curl -s "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":"ping"}],"max_tokens":5}'
```

### Fix

- **Rate limit / monthly cap.** Swap the bot to a different provider via `~/.openclaw/scripts/diversify-bots-free-providers.py`. Aim to spread the council across ≥4 providers.
- **Transient outage.** Wait 5-10 minutes. If it persists, swap that bot to local fallback (`~/.openclaw/scripts/swap-to-local.py` for that bot only).
- **Crashed gateway.** `launchctl kickstart -k gui/$(id -u)/ai.<bot>.gateway`.

## Bot replies with the wrong identity

### Symptom

`@drnonbob_bot` posts a message starting with `[Musk first-principles + Fuller systems]:` (Tenet's prefix).

### Cause

The bot's SOUL doesn't have the FIRST-6-CHARS rule, OR the model is leaking another bot's identity from the deliberation context (it sees Tenet's posts in the chat history and "becomes" Tenet).

### Fix

In Bob's SOUL, add (above SUBSTRATE):

```
## CRITICAL — FIRST-6-CHARS RULE (anti-roleplay enforcement)

Your FIRST CONTRIBUTION to a session MUST start with the literal
6 characters: `[Freud` (i.e., `[Freud unsaid + ground sense]:` in full).

If your first 6 characters are anything else — especially `**Bob`,
`**Ten`, `**Han`, `**Ana`, `**Civ`, `**Ott`, `**Rad`, `**Pip`,
`**noN`, or `[Musk`, `[Kant`, `[Mill`, `[Doug`, `[Pilg`, `[Jung` —
you have failed identity. Re-compose immediately starting with
`[Freud unsaid + ground sense]:`. No exceptions.
```

Replace `[Freud` and `Bob` with whichever bot is misbehaving.

This rule has been observed to fix identity leaks even on small models. It works because the *literal first 6 characters* is mechanical — the bot doesn't need to "understand" the rule, just match the constraint.

## Bot refuses media tasks ("I cannot generate a podcast")

### Symptom

You message: *"make a podcast about waiting."* Bob replies: *"I am not able to generate a podcast based on the provided article."*

### Cause

Bob's SOUL doesn't have the CONTENT-vs-ACTION distinction. He thinks "podcast = render = not my job" and refuses the whole request, when in fact he was supposed to bring the *content* (Freudian take on waiting) while Otto handles the rendering.

### Fix

Splice the TASK ROUTING addendum into Bob's SOUL. Full text in [`04-task-routing.md`](04-task-routing.md). Or run:

```bash
~/.openclaw/scripts/splice-task-routing.py --bot bob
```

After restart, Bob should post `[Freud unsaid + ground sense]: On waiting: ...` with actual content. Otto handles the MP3 separately.

## Bot posts duplicates ("3-layer cake" three turns in a row)

### Symptom

Pip posts the same *"The X is a 3-layer cake: 1. Surface 2. Middle 3. Foundation"* framing three times in 30 seconds, often verbatim.

### Cause

Pip's SOUL doesn't have ANTI-DUPLICATE. The bot is responding to each new bot's post in the chat as if it's a fresh question, and re-using its template each time.

### Fix

Splice the ANTI-DUPLICATE addendum (full text in [`04-task-routing.md`](04-task-routing.md)). Or run:

```bash
~/.openclaw/scripts/splice-task-routing.py --bot pip
```

After restart, Pip's first contribution still starts with his lens prefix. Subsequent contributions in the same turn are limited to engagement tokens (`EXPAND @<bot>:` / `QUALIFY @<bot>:` / `CONCEDE @<bot>:` / `STAND vs @<bot>:` / `PASS (reason: ...)`).

For full enforcement, also implement the orchestrator-side dedupe layer (Levenshtein 85% similarity → drop). Without that layer, the SOUL rule is "honor system" — most bots obey it; some don't. With the layer, violations are silently dropped.

## Otto promises but never delivers

### Symptom

Tenet routes a task to Otto. Otto posts: *"I've got this. Want to see it?"* And then nothing — no skill invocation, no artefact, no PASS, just silence. Or 5 minutes later, more *"I've got this..."* messages.

### Cause

Otto's SOUL doesn't have EXECUTOR DISCIPLINE. The model is in "agreeable assistant" mode — saying yes to look helpful, then drifting because it has no concrete next-step plan.

### Fix

Splice the EXECUTOR DISCIPLINE addendum (full text in [`04-task-routing.md`](04-task-routing.md)).

The key constraint: **one line of intent → invoke skill → deliver result**. No padding. If no skill matches, `PASS (reason: no skill registered for X)`.

## Radar floods chat with "Still working..."

### Symptom

Radar posts `⏳ Still working... (10 min elapsed — iteration 5/60, receiving stream response)` 5+ times in a single turn. Sometimes the final output is also gibberish (`Get res not run needs is null as atomic...`).

### Causes

1. **Streaming progress is too chatty.** Radar's hermes config emits a progress message every iteration; needs to be capped.
2. **Model output degraded.** Gemini Flash occasionally produces token-stream garbage when stressed (rate limit edge cases).

### Fix

Splice the Radar-specific TASK ROUTING + ANTI-STREAM-FLOOD addendum (text in [`04-task-routing.md`](04-task-routing.md)). It caps "still working" messages at 1/min, max 3/turn, and tells Radar to abort with `✗ failed: model output degraded` if his own output is going wonky.

For the underlying Gemini quota issue:
```bash
# Check Gemini's current free-tier usage at:
# https://console.cloud.google.com/apis/dashboard?project=<your-project>
# If Hermes is the heavy user, top up to paid tier (~$1-2/mo).
```

## All bots silent after a Telegram outage

### Symptom

Group chat went quiet. No bots responding. Telegram itself works (you can DM friends).

### Cause

Telegram bot polling is sticky after API hiccups. Each bot's gateway may have stuck on a `getUpdates` call.

### Fix

```bash
for b in ana bob civic hannah pip tenet non; do
  launchctl kickstart -k gui/$(id -u)/ai.$b.gateway
done
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway   # Otto
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway     # Radar
```

Wait 30 sec. Council should be back.

## OpenRouter free models 429ing constantly

### Symptom

A bot on `openrouter/<model>:free` returns 429 every other call. Or *"temporarily rate-limited upstream."*

### Cause

OR's `:free` models are shared across ALL users globally. When the upstream provider (Together / Deepinfra / Chutes) is saturated, your free request gets bumped.

### Fix

- **Top up $10 in OR.** This unlocks the 1000 free-req/day cap from 50/day. The $10 sits as balance; only spent if you also use paid models.
- **Or move that bot to a non-OR provider.** DashScope, Groq, or NVIDIA NIM for the same model class.

## DashScope key isn't working ("does not exist or you do not have access")

### Symptoms

```
✗ qwen3-30b-a3b-instruct → The model `qwen3-30b-a3b-instruct` does not exist or you do not have access to it.
```

### Causes

1. Model name typo (Alibaba names are precise — `qwen-turbo-latest` not `qwen-turbo`).
2. Model not enabled on your account region (some models are CN-only or region-locked).
3. You have the AccessKey ID/Secret pair, not a DashScope API key.

### Fix

- Check exact model names at https://help.aliyun.com/zh/model-studio/models or via `curl https://dashscope-intl.aliyuncs.com/compatible-mode/v1/models -H "Authorization: Bearer $DASHSCOPE_API_KEY"`.
- If wrong key type, get the right one: https://bailian.console.aliyun.com → Profile → API Key → Create my API key. The right key starts with `sk-`.
- If region-locked, retry with `--region cn` (for the China endpoint).

## Bot uses 100% of free monthly NVIDIA NIM quota in 3 days

### Cause

Each NIM model has 1000 req/month. If a single bot hammers one model (e.g. Llama 3.3 70B) it'll burn through fast.

### Fix

Spread across NIM's many models. Bob on `meta/llama-3.3-70b`, Otto on `mistralai/mistral-large-3-675b`, Hannah on `meta/llama-3.1-70b` — three separate quota buckets, 3000 req/month aggregate.

If you still need more, pay-per-use kicks in via NIM enterprise — or move that bot to OR paid (~$5-8/mo per heavily-used bot).

## Council generates a bias / culturally-tone-deaf reply

### Symptom

A bot says something insensitive. Comes from the model's training, not your SOUL.

### Fix

Two layers:

1. **Add a guardrail to the SOUL.** Just below SUBSTRATE:
   ```
   ## CULTURAL CARE
   - Never generalise about national/ethnic groups in a turn.
   - When the topic involves a culture, name a SPECIFIC instance (a person,
     a place, a moment) — never the abstract "X people are..." form.
   - If the room is heading toward a stereotype, PASS (reason: heading
     toward generalisation; needs a specific instance).
   ```

2. **Use a model trained on more diverse data.** Qwen series is multilingual and Asia-trained; can be a better fit for Asia-context council than Llama. DeepSeek similarly.

## When all else fails

```bash
# Roll the bot back to its last known good config
ls ~/.nanobot-<bot>/config.json.bak.*
cp ~/.nanobot-<bot>/config.json.bak.<timestamp> ~/.nanobot-<bot>/config.json
launchctl kickstart -k gui/$(id -u)/ai.<bot>.gateway
```

If you still can't get a bot working, kill it (disable via launchctl), let the rest of the council carry the load, and come back to that bot fresh in a day. Sometimes a bot's SOUL needs surgery, not patching.

→ End of docs. Back to [`README.md`](../README.md).
