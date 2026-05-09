# 02 — Setup quickstart

> Zero to first council message in ~30 minutes.

We'll walk through the smallest possible council: **3 bots** (Tenet, Ana, Otto), all on free providers. Once that works, scale up to all 9 by repeating the same steps.

## Prerequisites

- macOS or Linux. (Windows works in WSL2, untested.)
- Python 3.11+.
- A Telegram account.
- 30 minutes.

```bash
# Check Python
python3 --version    # must be 3.11 or newer

# Tools we'll need
brew install ffmpeg jq
pip install --user nanobot
```

## Step 1 — Make the Telegram group + 3 bots

1. Open Telegram. Create a new group called *"My Council"* (or whatever).
2. Open a DM with [@BotFather](https://t.me/BotFather).
3. Run `/newbot` three times, creating:
   - `@yourname_tenet_bot`
   - `@yourname_ana_bot`
   - `@yourname_otto_bot`
4. Save each bot token. They look like `8543196604:AAH...` — keep them in a notes file for now (we'll move to env files in step 4).
5. Add each bot to your group. Promote each to admin (so it can read all messages, not just `@`-mentions).

## Step 2 — Get your free LLM provider keys

Sign up for these (15 minutes total). All are free and don't require a credit card on signup:

| Provider | What you get | Where |
|---|---|---|
| **Groq** | Llama 3.3 70B + DeepSeek R1 distill, 30 RPM free | https://console.groq.com |
| **NVIDIA NIM** | Llama 3.3 70B + Mistral Large 3, 1000 req/month/model | https://build.nvidia.com |
| **Google AI Studio** | Gemini 2.5 Flash, 1500 RPD free | https://aistudio.google.com/apikey |

For the chair (Tenet) we'll use Alibaba DashScope's Qwen3-Max — best free-tier reasoner. Sign up:

| Provider | What you get | Where |
|---|---|---|
| **Alibaba DashScope** | Qwen3-Max + qwen-flash + qwen-turbo, 1M tokens/model free + cheap pay-as-you-go | https://bailian.console.aliyun.com → Profile → API Key → Create |

(If you don't want to use DashScope, replace Tenet with `groq/llama-3.3-70b-versatile` for a fully free council.)

## Step 3 — One config file per bot

Each nanobot lives in its own directory and has one `config.json`. Here's the pattern. Replace placeholders with real values; **never commit these files** (they have your bot tokens).

`~/.nanobot-tenet/config.json`:

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.nanobot-tenet/workspace",
      "model": "dashscope/qwen3-max",
      "maxTokens": 4096,
      "temperature": 0.7
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_TENET_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID", "YOUR_GROUP_CHAT_ID"]
    }
  },
  "providers": {
    "dashscope": {
      "apiKey": "sk-YOUR-DASHSCOPE-KEY",
      "apiBase": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    }
  },
  "gateway": {"host": "0.0.0.0", "port": 18790}
}
```

For Ana, change `model` to `groq/llama-3.1-8b-instant`, swap `dashscope` → `groq`, change the port. For Otto, use `nvidia_nim/meta/llama-3.3-70b-instruct` and keep tools enabled (Otto needs file/web/exec permissions in his providers — see the implementation repo for the full template).

Find your **user ID** by messaging [@userinfobot](https://t.me/userinfobot). Find your **group chat ID** by adding [@RawDataBot](https://t.me/rawdatabot) to the group temporarily; it'll print the chat ID (negative for groups).

## Step 4 — Drop in the SOUL prompts

Each bot's directory has a `workspace/SOUL.md` that becomes the system prompt. Copy from [`examples/souls/`](../examples/souls/):

```bash
mkdir -p ~/.nanobot-tenet/workspace ~/.nanobot-ana/workspace ~/.nanobot-otto/workspace

# Get the SOUL templates
curl -L https://raw.githubusercontent.com/nonarkara/dr-non-agentic-ai-council/main/examples/souls/Tenet.SOUL.md \
  -o ~/.nanobot-tenet/workspace/SOUL.md

curl -L https://raw.githubusercontent.com/nonarkara/dr-non-agentic-ai-council/main/examples/souls/Ana.SOUL.md \
  -o ~/.nanobot-ana/workspace/SOUL.md

curl -L https://raw.githubusercontent.com/nonarkara/dr-non-agentic-ai-council/main/examples/souls/Otto.SOUL.md \
  -o ~/.nanobot-otto/workspace/SOUL.md
```

Read each SOUL. It's the bot. You'll want to customise the substrate section (the cognitive base) to match your own thinking — the templates use Dr Non's. The face / thinker / lens prefix should stay as-is unless you're forking.

## Step 5 — Launch the gateways

```bash
NANOBOT_HOME=~/.nanobot-tenet nanobot gateway --bot-name Tenet &
NANOBOT_HOME=~/.nanobot-ana   nanobot gateway --bot-name Ana &
NANOBOT_HOME=~/.nanobot-otto  nanobot gateway --bot-name Otto &
```

Each starts polling Telegram for messages.

For permanent setups, write three launchd plists (macOS) or systemd units (Linux). See [`examples/launchd/`](../examples/launchd/) for templates.

## Step 6 — Test it

Open Telegram, message your group: *"What do you do when you feel unmotivated?"*

Within ~30 seconds you should see:

```
@yourname_tenet_bot:
[Musk first-principles + Fuller systems]: The unmotivated state is
the room asking for a smaller next move. Specifically: name one
concrete thing you can do in 90 seconds. ...

@yourname_ana_bot:
[Kant duty + James pragmatism]: The duty here is honesty about
the gap between intention and action. ...

@yourname_otto_bot:
NO_REPLY
```

Three voices. Different lenses. One specific question, three useful angles.

## Step 7 — Scale to 9

Repeat steps 3-5 for the remaining 6 bots (Civic, Hannah, Bob, Pip, noN, Radar). Use this provider allocation as a starting point — it's what's running live in Dr Non's council:

| Bot | Provider | Model |
|---|---|---|
| Tenet | DashScope | `qwen3-max` |
| Civic | DashScope | `qwen-flash` |
| Pip | DashScope | `qwen-flash` |
| Hannah | DashScope | `qwen-turbo-latest` |
| Ana | Groq | `llama-3.1-8b-instant` |
| Bob | OpenRouter (paid, ~$5/mo) | `deepseek/deepseek-chat-v3.1` |
| noN | OpenRouter (paid, ~$3/mo) | `meta-llama/llama-3.3-70b-instruct` |
| Otto | NVIDIA NIM | `meta/llama-3.3-70b-instruct` |
| Radar | Gemini | `gemini-2.5-flash` |

→ Why this allocation: [`05-providers-zero-cost.md`](05-providers-zero-cost.md).

## Common first-day problems

- **No bots reply.** Check that each bot is admin in the group (group privacy mode in BotFather: turn it OFF for group bots).
- **Wrong bot answers.** Two bots have the same lens prefix. Check SOUL files — the IDENTITY RULE block should say each bot's prefix is unique.
- **All bots answer with the same generic preamble.** SOULs aren't loading. Check `workspace/SOUL.md` exists and `NANOBOT_HOME` is set when you launch.
- **HTTP 429 from a provider.** Free tier rate limit hit. Diversify — move that bot to a different provider. See [`05-providers-zero-cost.md`](05-providers-zero-cost.md).
- **Otto says "I've got this. Want to see it?" then nothing happens.** SOUL needs the EXECUTOR DISCIPLINE addendum. See [`04-task-routing.md`](04-task-routing.md).
- **Bots post duplicate messages.** SOUL needs the ANTI-DUPLICATE addendum. Same doc.

## What's next

Once the 3-bot council works, expand to 9. Once 9 works, add skills (podcast generation, video generation, image generation) — see [`08-skills.md`](08-skills.md).

Your first month, expect to tweak SOULs daily. Don't worry about getting it right; iterate. Read the deliberation logs at the end of each day, see which lens missed what, edit the SOUL, restart the bot.

→ [`03-the-bots.md`](03-the-bots.md) — full reference for each justice's role and SOUL.
