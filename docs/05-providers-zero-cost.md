# 05 — Provider stack at $0 (the cost-saving playbook)

> Where to get free LLM inference, how to spread it across providers so no single rate limit kills the room, and what to actually pay for when free isn't enough.

This is the most important practical doc in the repo. **The whole council is designed around the cost stack.**

## The principle: diversify across providers

Every LLM provider has a free tier. Most people pick one provider (usually OpenAI), burn through the free tier in a week, and conclude "AI is expensive."

The council does the opposite: **use ~5 providers in parallel, allocate one bot per provider, and the aggregate free capacity dwarfs what any single provider gives you.** Plus, when one provider has an outage or rate-limits, only the bots on that provider stutter — the rest of the room keeps running.

```
                          THE PROVIDER FAN-OUT

   ┌──────────────────────────────────────────────────────────────┐
   │                       9 council bots                         │
   └─────────┬──────────┬──────────┬──────────┬──────────┬────────┘
             │          │          │          │          │
             ▼          ▼          ▼          ▼          ▼
        ┌──────────┐ ┌────────┐ ┌──────┐ ┌──────────┐ ┌──────────┐
        │ DashScope│ │ Groq   │ │ NIM  │ │ Gemini   │ │OpenRouter│
        │ (Alibaba)│ │ (free) │ │(free)│ │ (free)   │ │ (paid    │
        │  4 bots  │ │ 1 bot  │ │ 2bot │ │  1 bot   │ │  passthr)│
        │  ~$5-15  │ │   $0   │ │  $0  │ │    $0    │ │  ~$8/mo  │
        └──────────┘ └────────┘ └──────┘ └──────────┘ └──────────┘

   Total: ~$15-25/month for a 9-bot daily-use council.
   Strict-zero variant: $0, slightly weaker chair reasoning.
```

## The provider rundown

### Free, no credit card required

#### Groq

```
Free tier:        30 RPM, ~14400 RPD, multiple models
Models:           llama-3.3-70b-versatile, llama-3.1-8b-instant,
                  deepseek-r1-distill-llama-70b, mixtral, gemma2
Endpoint:         https://api.groq.com/openai/v1
Sign up:          https://console.groq.com
Strengths:        Fastest inference (sub-second latency), big variety
Weaknesses:       Cloudflare blocks some HTTP clients (use curl, not urllib);
                  free tier saturates around 7-9pm Bangkok time
```

Groq is the bread-and-butter free provider. We use it for **Ana** (`llama-3.1-8b-instant` for short turns).

#### NVIDIA NIM

```
Free tier:        1000 requests/month per model
Models:           meta/llama-3.3-70b-instruct,
                  mistralai/mistral-large-3-675b-instruct,
                  many more — NVIDIA hosts ~50 models
Endpoint:         https://integrate.api.nvidia.com/v1
Sign up:          https://build.nvidia.com (NVIDIA developer account)
Strengths:        Big-context (128K+), good model variety, OpenAI-compatible
Weaknesses:       1K/month is moderate; works best when one bot doesn't
                  hammer one model
```

We use NIM for **Otto** (executor with tool-call reliability requirements). The tool-calling JSON format is well-handled by NIM's Llama 70B.

#### Google AI Studio (Gemini)

```
Free tier:        15 RPM, 1500 RPD
Models:           gemini-2.5-flash (fast), gemini-2.5-pro (slower, smarter)
Endpoint:         https://generativelanguage.googleapis.com/v1beta/openai
Sign up:          https://aistudio.google.com/apikey
Strengths:        Massive 1M token context window, OpenAI-compatible
Weaknesses:       Free tier shared across ALL apps using that key —
                  if hermes also uses it for personal-assistant work,
                  you'll hit the cap mid-day
```

We use Gemini for **Radar** (the secretary with hermes-style tool access).

### Free with credit card on file (cheap pay-as-you-go beyond grants)

#### Alibaba DashScope (Model Studio / Bailian)

```
Free tier:        1 million tokens/model on signup (one-time grant)
Models:           qwen3-max (top-tier), qwen-max-latest, qwen-plus-latest,
                  qwen2.5-72b-instruct, qwen-turbo-latest, qwen-flash,
                  qwen-coder-plus
Endpoint:         https://dashscope-intl.aliyuncs.com/compatible-mode/v1
                  (use --region cn for the mainland endpoint)
Sign up:          https://bailian.console.aliyun.com
                  Profile → API Key → Create my API key (sk-...)
Strengths:        qwen3-max is genuinely Claude-Sonnet-class; pay-per-use
                  is dirt cheap (~$0.0024/1K input for qwen3-max,
                  ~$0.0001/1K for qwen-flash); huge context windows
Weaknesses:       Need a credit card for the post-grant pay-per-use;
                  the AccessKey ID/Secret is a different (more dangerous)
                  key type — get the API key, not the AccessKey
```

**Important:** DashScope has TWO key systems. Get the right one:
- **DashScope API key** (single `sk-...` token) — this is what you want.
- **AccessKey ID + Secret** (pair of strings) — for full Aliyun Cloud SDK; **DO NOT use**, it grants unrestricted permissions to your entire account. If you accidentally created one, disable it.

We use DashScope for **Tenet** (`qwen3-max` — the chair gets the heavy brain) plus **Civic, Pip, Hannah** (`qwen-flash` / `qwen-turbo-latest` — cheap variants for the lighter reasoners).

#### OpenRouter

```
Free tier:        50 free-model requests/day if account balance < $10
                  1000 free-model requests/day if balance ≥ $10
                  (the "$10 wall" — fund $10 once, the cap upgrades)
Models (free):    deepseek/deepseek-chat-v3.1:free,
                  meta-llama/llama-3.3-70b-instruct:free,
                  qwen/qwen-3-32b:free, others
Models (paid):    Almost everything — Claude, GPT, DeepSeek, Kimi, Qwen,
                  Llama, Gemini — at ~5% margin over upstream pricing
Endpoint:         https://openrouter.ai/api/v1
Sign up:          https://openrouter.ai
Strengths:        Single API for everything; cheap insurance against
                  any one provider going down
Weaknesses:       Free models are shared across all OR users globally;
                  prompts on free models may be logged by upstream for
                  training (privacy concern for sensitive content)
```

We use OR (paid) for **Bob** (`deepseek/deepseek-chat-v3.1`, ~$5-8/mo) and **noN** (`meta-llama/llama-3.3-70b-instruct`, ~$2-3/mo) — the two bots that were hitting NIM's monthly cap.

### Useful but secondary

| Provider | Free tier | Strength |
|---|---|---|
| **Cerebras** | 30 RPM Llama 3.3 70B at 1700 tok/s | Faster than Groq |
| **SambaNova** | 10 RPM Llama 3.1 405B free | Bigger model than 70B |
| **GitHub Models** | Free for devs (uses GitHub login) | Includes GPT-4o, Claude Sonnet |
| **Cloudflare Workers AI** | 10K neurons/day | Generous, multi-model |
| **Zhipu (智谱) GLM-4 Flash** | Generous | Chinese provider, separate quota pool |
| **Mistral La Plateforme** | Free experimental tier | Native Mistral |

These are good *secondary* providers. Sign up for any if you want extra capacity, but the 5 above (DashScope, Groq, NIM, Gemini, OR) cover the council comfortably.

## The current allocation — copy this

```
| Bot     | Provider          | Model                                  | $/mo    |
|---------|-------------------|----------------------------------------|---------|
| Tenet   | DashScope         | qwen3-max                              | $5-15   |
| Civic   | DashScope         | qwen-flash                             | <$1     |
| Pip     | DashScope         | qwen-flash                             | <$1     |
| Hannah  | DashScope         | qwen-turbo-latest                      | <$1     |
| Ana     | Groq              | llama-3.1-8b-instant                   | $0      |
| Bob     | OpenRouter (paid) | deepseek/deepseek-chat-v3.1            | $5-8    |
| noN     | OpenRouter (paid) | meta-llama/llama-3.3-70b-instruct      | $2-3    |
| Otto    | NVIDIA NIM        | meta/llama-3.3-70b-instruct            | $0      |
| Radar   | Gemini            | gemini-2.5-flash                       | $0      |
|         |                   |                                  Total | $15-25  |
```

**Why this allocation:**
- **Tenet on qwen3-max** — chair gets the heavy brain. Worth the ~$10/mo.
- **Civic/Pip/Hannah on qwen-flash/turbo** — cheap reasoners for the lighter lenses. <$1/mo each.
- **Ana on Groq llama-3.1-8b-instant** — Ana's turns are short; small model is fine; free tier covers it.
- **Bob/noN on OR paid** — these were the bots hitting NIM's monthly cap; OR pay-as-you-go is reliable.
- **Otto on NIM** — executor with tool calls; NIM's Llama 70B handles tool-call JSON well.
- **Radar on Gemini** — 1M context window matters for the secretary's summarisation work.

## The strict-zero variant

If you want **$0/month sustained**, replace the paid bots:

```
| Bot     | Provider     | Model                              | $/mo |
|---------|--------------|------------------------------------|------|
| Tenet   | Groq         | llama-3.3-70b-versatile            | $0   |
| Civic   | DashScope    | qwen-flash (free quota)            | $0*  |
| Pip     | DashScope    | qwen-flash (free quota)            | $0*  |
| Hannah  | DashScope    | qwen-turbo-latest (free quota)     | $0*  |
| Ana     | Groq         | llama-3.1-8b-instant               | $0   |
| Bob     | NVIDIA NIM   | meta/llama-3.3-70b-instruct        | $0   |
| noN     | NVIDIA NIM   | mistralai/mistral-small-4-119b     | $0   |
| Otto    | NVIDIA NIM   | meta/llama-3.3-70b-instruct        | $0   |
| Radar   | Gemini       | gemini-2.5-flash                   | $0   |
|         |              |                              Total | $0*  |
* DashScope free token grant lasts ~1 month at council load; after
  that, ~$2/mo total for the 3 cheap bots.
```

The trade-off vs the $15-25 setup:
- Tenet on Llama 3.3 70B is ~80% as good as qwen3-max for routing/synthesis. Noticeably weaker on subtle pattern questions.
- NIM 1K/month/model = with 3 bots sharing Llama 3.3 70B, you'll hit the cap by day 25. Move them to different NIM models (Mistral Large 3, Llama 3.1 70B) to spread.
- No OR insurance — if Groq has a Cloudflare hiccup, half the council goes silent.

If you can afford $15/mo, do the paid setup. If not, this works.

## Cost-saving tricks

### 1. The `$10 wall` on OpenRouter

Free models on OR are rate-limited at 50 req/day if you have < $10 in your account, **1000 req/day if you have ≥ $10**. Top up exactly $10 once → tier upgrade is permanent (until balance drops below $10). The $10 is also insurance — sits there as fallback budget if a primary provider dies.

### 2. Use `qwen-flash` and `qwen-turbo-latest` for non-critical bots

DashScope's cheapest models are absurdly priced — `qwen-flash` is ~$0.0001/1K input, $0.0003/1K output. The whole council on these would cost <$2/month. Reserve qwen3-max for the chair only.

### 3. Don't run hermes when nanobot will do

Hermes is heavy — big context, MCP servers, daemons. It uses 5-10× the LLM tokens of a nanobot per turn. Use hermes only for Radar (or your main personal assistant). Every other council bot = nanobot.

### 4. Use `picoclaw` for prototypes

When you're testing a new bot personality, run it as a picoclaw first (one process, no tool integrations, minimal SOUL). Iterate the personality at $0 of LLM cost. When it's good, promote it to nanobot.

### 5. Free-tier round-robin via the gateway

If you sign up for Cerebras + SambaNova + Groq, all three serve `llama-3.3-70b-versatile` (or close cousins) for free. You can build a wrapper that round-robins between them on 429, multiplying your effective rate limit by 3×. This is a future improvement; nanobot doesn't have native fallback chains today.

### 6. Cache identical prompts

Council deliberations have a lot of repeating context (the SOUL prompt + Dr Non's substrate + the deliberation log so far). Some providers (Anthropic, OpenAI) offer prompt caching at 90% off. If you move to a paid setup, prompt caching alone can cut bills 5×.

### 7. Track usage per provider

Run `~/.openclaw/scripts/check-provider-usage.py` (or check each provider's dashboard) weekly. If one is approaching its cap, swap a bot to a different provider before the cap hits.

## The signups, in priority order

If you're starting fresh, sign up in this order:

1. **Telegram + BotFather** — make 9 bot tokens. Free.
2. **Groq** — 5 minutes. Email signup. Free 30 RPM.
3. **NVIDIA NIM** — 5 minutes. Developer account. Free 1K/month/model.
4. **Google AI Studio** — 2 minutes. Uses your Gmail. Free 1500 RPD.
5. **Alibaba DashScope** — 10 minutes. Phone or email. **Get the API key, not the AccessKey.** 1M tokens/model free.
6. **OpenRouter** — 5 minutes. Top up $10 to unlock the 1000 free req/day tier. Optional but recommended for insurance.

Total: ~30 minutes of signups. After that, you have enough capacity for a 9-bot council running 24/7.

→ Next: [`06-local-fallback.md`](06-local-fallback.md) — when even the cloud isn't enough.
