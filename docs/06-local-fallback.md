# 06 — Local fallback: phi4-mini via Ollama

> When every cloud provider goes down on the same day. Or you're on a plane.
> Or you just don't trust any of them with the next 10 minutes of thinking.

## Why local matters

Cloud providers are reliable enough — usually. But the failure modes are correlated: a Cloudflare incident takes out Groq, OpenRouter, and a chunk of NVIDIA in the same hour. A Google Cloud regional outage takes Gemini. AliCloud's been known to have international-endpoint hiccups.

The council is built to survive one provider going down — but not all of them.

**Local fallback is the doomsday answer.** A small model on your Mac that can answer in 5-10 seconds, no internet needed, free forever. It won't match qwen3-max, but it can handle the chair-routing job long enough for the cloud to come back.

## What we use

[**Microsoft phi-4-mini-instruct**](https://huggingface.co/microsoft/Phi-4-mini-instruct).

```
Parameters:    3.8 B
Disk size:     ~2.4 GB (Q4 quant)
RAM needed:    ~5 GB during inference
Speed on M2:   ~25-40 tokens/sec
Speed on M5:   ~80-120 tokens/sec
Quality:       comparable to GPT-3.5 / Llama-3-7B for short reasoning
```

Why phi-4-mini specifically:
- **Tiny enough to run on any modern Mac** (16 GB RAM is plenty).
- **Good at structured short-form output** — JSON, lens-prefixed responses, decision pins.
- **Fast** — sub-5-second turn time on Apple Silicon.
- **Open weights** — Microsoft MIT-licensed; no API key, no data leaves your machine.

For the council's chair role (Tenet) when the cloud is down, phi-4-mini is good enough to route, summarise, and pin decisions. Not good enough to take a deep philosophical position — but the deep positions can wait until the cloud is back.

## Setup (one time, 5 minutes)

### Option A: Ollama (recommended)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
# or: brew install ollama

# 2. Pull the model
ollama pull phi4-mini:latest

# 3. Start the Ollama server (it auto-starts on macOS after install)
ollama serve  &

# 4. Test it
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi4-mini:latest",
    "messages": [{"role": "user", "content": "Say pong."}]
  }'
```

You should see a JSON response with `"content": "pong"` (or close). If you see that, the local fallback works.

### Option B: LM Studio

If you prefer a GUI, [LM Studio](https://lmstudio.ai) gives you a one-click model browser, server, and prompt playground. Pull `Phi-4-mini-instruct-Q4_K_M.gguf` from their model hub, click "Start Server" — same OpenAI-compatible endpoint at `http://localhost:1234/v1`.

### Option C: MLX (Apple Silicon native, fastest)

For raw speed on M-series Macs, use [MLX](https://github.com/ml-explore/mlx-examples):

```bash
pip install mlx-lm
python -m mlx_lm.server --model microsoft/Phi-4-mini-instruct
```

MLX runs ~30% faster than Ollama on Apple Silicon. Trade-off: less polished tooling.

## Wiring the council to fall back

Nanobot doesn't have a built-in fallback chain (single model per bot). To add local fallback, you have three options:

### Option 1 — Manual swap on cloud outage

When you notice cloud failures, run a script that swaps every bot to phi4-mini. When the cloud is back, swap them back. The simplest, but requires you to be present.

```bash
# Save the helper script
cat > ~/.openclaw/scripts/swap-to-local.py <<'EOF'
#!/usr/bin/env python3
import json, shutil, subprocess
from pathlib import Path

BOTS = ["ana","bob","civic","hannah","pip","tenet","non"]
LOCAL_MODEL = "openai/phi4-mini:latest"   # litellm convention
LOCAL_BASE = "http://localhost:11434/v1"

for bot in BOTS:
    if bot == "tenet":     cfg_path = Path.home()/".nanobot/config.json"
    elif bot == "non":     cfg_path = Path.home()/".nanobot-non/config.json"
    else:                  cfg_path = Path.home()/f".nanobot-{bot}/config.json"
    if not cfg_path.exists(): continue
    cfg = json.loads(cfg_path.read_text())
    cfg.setdefault("providers",{}).setdefault("openai",{})
    cfg["providers"]["openai"]["apiBase"] = LOCAL_BASE
    cfg["providers"]["openai"]["apiKey"] = "ollama-no-auth"
    cfg["agents"]["defaults"]["model"] = LOCAL_MODEL
    cfg_path.write_text(json.dumps(cfg, indent=2)+"\n")
    label = f"ai.{bot}.gateway"
    subprocess.run(["launchctl","kickstart","-k",
                     f"gui/{subprocess.run(['id','-u'],capture_output=True,text=True).stdout.strip()}/{label}"])
    print(f"  ✓ {bot} → local phi4-mini")
EOF
chmod +x ~/.openclaw/scripts/swap-to-local.py
```

Then when the cloud is down: `~/.openclaw/scripts/swap-to-local.py`.

### Option 2 — A reverse-proxy with fallback

Run a small local proxy (FastAPI app, ~30 lines) that:
- Receives OpenAI-compatible requests
- Tries the cloud provider first (5s timeout)
- Falls back to local Ollama if cloud fails
- Returns whichever response succeeds

Point all bot configs at `http://localhost:9999/v1`. Bots never know which brain answered. Setup is fiddlier but the failover is automatic.

A starter version of this is in [`scripts/llm-fallback-proxy.py`](../scripts/llm-fallback-proxy.py).

### Option 3 — Just keep local always-on for one bot

If you want local in the rotation full-time, point **noN** (the easter-egg bot — low load, occasional speaker) at phi4-mini. He'll only post when the shadow is loud, so the slower local model doesn't bottleneck the council. Bonus: noN's contributions are entirely private to your machine.

```json
"agents": {
    "defaults": {
        "model": "openai/phi4-mini:latest"
    }
},
"providers": {
    "openai": {
        "apiKey": "ollama-no-auth",
        "apiBase": "http://localhost:11434/v1"
    }
}
```

## Larger local models, when you outgrow phi4-mini

When you have 32+ GB of RAM and can spare the disk space, consider:

| Model | Size | Speed (M2 Max) | Quality |
|---|---|---|---|
| `phi4-mini:latest` (3.8B) | 2.4 GB | 25-40 tok/s | GPT-3.5-class |
| `qwen2.5-7b-instruct` | 4.5 GB | 30-50 tok/s | Llama 3 8B-class |
| `mistral-small-3:24b` | 14 GB | 12-20 tok/s | Llama 3 70B-class |
| `llama-3.3:70b-q4` | 40 GB | 4-8 tok/s | qwen-plus class |

Anything bigger than 24B will swap to disk on a 32 GB Mac and run very slowly. **For a council, you want fast turns more than smart turns** — pick speed over depth on local.

## Quality reality check

phi4-mini is not qwen3-max. Specifically:
- It will miss nuanced pattern-bias questions Hannah would catch.
- It will write technically-correct-but-flat synthesis when Tenet would write something sharper.
- It will fabricate cleanly when it shouldn't (the SOUL anti-fabrication rules still help, but matter more on a small model).

For routine council deliberation in a cloud outage, that's fine. For high-stakes decisions, wait for the cloud.

## When to actually use this

- **Plane / no internet.** Set bots to local before takeoff.
- **Travel through firewalls.** Some networks block AliCloud / Anthropic. Local always works.
- **Privacy-sensitive deliberation.** When you don't want the prompt logged anywhere — local-only.
- **Provider outage.** Run the swap-to-local script; council keeps responding while you wait for the cloud to recover.
- **Daily-use noN.** Permanently route the easter-egg bot to local; he's low-load and benefits from absolute privacy.

→ Next: [`07-the-frameworks.md`](07-the-frameworks.md) — picoclaw vs nanobot vs openclaw vs hermes, when to use each.
