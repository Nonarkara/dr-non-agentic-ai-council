# Costs — what this council actually costs to run

> Real numbers from May 2026, verified against my live bills.

## TL;DR

```
Daily-use 9-bot council:                ~$15-25/month
Strict-zero variant (slightly weaker):  ~$0/month
+ optional skills (podcast, video, etc): pay-per-use, ~$0.25/artefact
```

For comparison:
```
Manus.ai Pro subscription:              $200/month
ChatGPT Team:                           $25/seat/month  (one user, one model)
Claude Pro:                             $20/month       (one user, one model)
GPT-4o API at council load:             ~$80-120/month  (do the math)
```

The council is **5-10× cheaper** than the next-cheapest "smart agent" option, with one user owning the whole stack.

## Where the $15-25 goes

```
| Bot     | Provider          | Model                              | $/mo    |
|---------|-------------------|------------------------------------|---------|
| Tenet   | DashScope         | qwen3-max                          | $5-15   |
| Civic   | DashScope         | qwen-flash                         | <$1     |
| Pip     | DashScope         | qwen-flash                         | <$1     |
| Hannah  | DashScope         | qwen-turbo-latest                  | <$1     |
| Bob     | OpenRouter (paid) | deepseek/deepseek-chat-v3.1        | $5-8    |
| noN     | OpenRouter (paid) | meta-llama/llama-3.3-70b-instruct  | $2-3    |
| Ana     | Groq              | llama-3.1-8b-instant               | $0      |
| Otto    | NVIDIA NIM        | meta/llama-3.3-70b-instruct        | $0      |
| Radar   | Gemini            | gemini-2.5-flash                   | $0      |
|         |                   |                              Total | $15-25  |
```

The variance ($15 vs $25) depends on how heavily you use Tenet specifically. The chair gets the heavy brain (qwen3-max) and his cost scales with how much synthesis he's doing. Casual chair use (~30 turns/day): ~$5/month. Heavy use (~150 turns/day): ~$15/month.

## What's free, and why

The "$0" bots aren't free in some grace-period sense. They're permanently free as long as you stay under the rate limits:

- **Groq:** 30 RPM, ~14400 requests/day. Ana's load is well under this.
- **NVIDIA NIM:** 1000 requests/month per model. Otto on Llama 3.3 70B uses ~600/month.
- **Gemini 2.5 Flash:** 1500 requests/day. Radar uses ~400/day.

If any of those bots' loads grow, the next move is to **swap to a different free provider**, not to start paying. Free capacity across 5 providers is huge.

## What the skills cost (pay-per-artefact)

Skills run on demand, not 24/7. Each generates one artefact, costs you that artefact's input/output tokens.

| Skill | Cost/artefact | What it costs |
|---|---|---|
| `tiktok-wisdom` | ~$0.25 | gpt-4o-mini script (~$0.005) + ElevenLabs voice (~$0.20-0.30) + ffmpeg (free) + Met art (free) |
| `blog-to-podcast-pipeline` | ~$0.50 | gpt-4o-mini script + ElevenLabs 2 voices + DALL-E cover |
| `council-image-gen` | ~$0.04 | DALL-E 3 single image (or ~$0.01 with Flux) |
| `pdf-publisher` | $0 | Quarkdown — open-source, runs locally |
| `epub-publisher` | $0 | Pandoc-based, runs locally |
| `card-to-google-contact` | $0 | Google Vision OCR free tier + Contacts API |
| `gdrive-save` | $0 | Drive API |
| `gmail-send` | $0 | Gmail API |
| `media-download` | $0 | yt-dlp |

So if you make 10 wisdom videos, 3 podcasts, 5 cover images, and OCR 20 business cards in a month:
```
10 × $0.25 = $2.50
 3 × $0.50 = $1.50
 5 × $0.04 = $0.20
20 × $0    = $0
            ──────
            $4.20  total skills cost for the month
```

## The strict-zero variant

If you're committed to actual zero-dollar:

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
```

\* DashScope's 1M-token-per-model free grant lasts ~1 month at council load. After that the cheap bots cost ~$2/month combined for `qwen-flash` / `qwen-turbo-latest`. So strict-zero is honest for the first month, ~$2 sustained.

The trade-off vs the $15-25 setup:
- **Tenet on Llama 3.3 70B (Groq) is ~80% as good as qwen3-max** for routing/synthesis. Noticeably weaker on subtle pattern questions where the chair's job is to ask the question nobody asked.
- **NIM has a 1K/month/model cap.** With 3 bots sharing Llama 3.3 70B, you'll hit the cap by day 25. Spread across NIM's other models (Mistral Large 3, Llama 3.1 70B) to avoid this.
- **No OR insurance.** If Groq has a Cloudflare incident, half the council goes silent.

For most users: **pay the $15-25.** It buys reliability + a sharper chair, and the friction of always-debugging-rate-limits eats more time than the money saved.

For students / strict $0 doctrine: **the strict-zero variant works.** Just don't expect Manus-grade reliability — expect "free tools, free trade-offs."

## The local-fallback option

Adds $0/month and ~5 GB of disk space:

```
phi4-mini via Ollama:                    free
  ~5 GB model file
  ~5 GB RAM during inference
  25-40 tokens/sec on M2, 80-120 on M5
  Quality: GPT-3.5-class (good for chair routing, weak for deep reasoning)
```

→ See [`docs/06-local-fallback.md`](docs/06-local-fallback.md).

## What I won't pay for, and why

**Claude Pro / ChatGPT Plus subscriptions:** $20-25/month each. Single-model access from a web UI. No API. The council needs API access; subscriptions don't help.

**Manus.ai Pro:** $200/month. Get the same effect (and more transparency) from this council for 1/10th the cost.

**Anthropic / OpenAI API at heavy use:** great models, but at council load (~50 turns/day across 9 bots × ~3K tokens/turn = 1.35M tokens/day = 40M tokens/month) the API bills hit:
```
Claude Sonnet 4.5:     ~$120/month
GPT-4o-mini:           ~$8/month     (cheap, but less smart than qwen3-max)
GPT-4o:                ~$300/month
```

The council deliberately uses Asia-trained models (Qwen, DeepSeek) because they're 5-10× cheaper for similar reasoning quality on the kinds of questions Dr Non actually asks. There's no "Western model premium" worth $100+/month.

## What I will pay for, and why

**ElevenLabs voice cloning** ($5/month base + ~$0.30/min for voice synthesis). Worth it because nothing else sounds like Dr Non's voice when narrating wisdom videos. The whole point of the videos is *authenticity*; a generic voice would defeat that.

**OpenAI for skill drafting** (~$5-10/month total, scattered across skills like tiktok-wisdom and blog-to-podcast-pipeline). gpt-4o-mini is $0.15/M input, $0.60/M output — the cheapest reliable JSON-emitting model. Used for *script generation* (one-shot, low-token), not for *bot turns* (high-volume). Different cost profile.

**Cloudflare D1 / Workers** (~$0/month at current usage; potentially $5/month if I pubilsh much more). The council's "delivery queue" and the public site that hosts the daily retrospective live on Cloudflare. Free tier covers everything.

**No paid IDE / no paid linter / no paid CI.** GitHub Actions free tier covers the council's tests. VS Code is free. No subscription stack outside the LLM providers.

## Putting it all together

A typical month for me, May 2026:

```
LLM providers:
  DashScope (Tenet + 3 cheap bots)       $7.20
  OpenRouter (Bob + noN paid)            $9.40
  Groq (Ana, free)                       $0
  NVIDIA NIM (Otto, free)                $0
  Gemini (Radar, free)                   $0
                                       ───────
                                        $16.60

Skills (pay-per-artefact):
  ~12 tiktok-wisdom videos                $3.00
  ~4 podcasts                             $2.00
  ~8 cover images                         $0.32
  ~30 OCR contacts                        $0
                                       ───────
                                         $5.32

Other:
  ElevenLabs base + use                  $9.50
  OpenAI scattered (skills)              $4.80
                                       ───────
                                        $14.30

                                  ═════════════
                            Grand total:  $36.22
```

That's the realistic full-stack monthly cost — council + media production + voice + scripting. **One Manus.ai subscription is $200**, and gives you one big agent that won't tell you why it decided what it did.

The council costs 1/5th and gives you ten different angles on every question.
