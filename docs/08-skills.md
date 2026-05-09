# 08 — Skills (what Otto can actually do)

> The skill registry that turns a thinking council into a working one.

Skills are the council's hands. The thinkers debate; Otto invokes a skill and ships an artefact. Each skill is one Markdown SKILL.md + one Python script (typically ~500-1000 lines, single file).

## Why skills matter

A council that only deliberates is a podcast about decisions. A council that *also acts* is an assistant. Skills are the bridge: when Tenet routes a request as TASK MODE, Otto looks at his skill registry, matches the request shape, invokes the right skill, ships the result.

The skills below are the ones running in Dr Non's live council. Each is open source. Mix and match for your own setup.

## Media generation

### tiktok-wisdom

```
Input:    one short idea (text)
Output:   60-90 sec vertical 9:16 MP4 with public-domain art,
          your cloned voice, burned-in captions, end-card
Cost:     ~$0.25/video (gpt-4o-mini drafting + ElevenLabs voice;
          Met art + ffmpeg are free)
Trigger:  "make a tiktok about X", "wisdom video", "video this idea"
```

Pipeline: idea → script via gpt-4o-mini in your voice → 6-8 atmospheric visual cues → Met Museum API + Wikimedia Commons fetch → ffmpeg Ken Burns + crossfades → ElevenLabs cloned voice → captions → optional end-card → push to Telegram.

Has `--strict` mode that forbids the model from inventing content not traceable to your blog corpus. Has `--draft-only` HTML preview mode to iterate the script before paying for TTS. Has provider switching (mac-say / openai / eleven). Has stage caching so retries don't redo art fetching. All in one CLI.

→ Reference: [`agentic-ai-research/dr-non-diy-ai-council` PR #9](https://github.com/agentic-ai-research/dr-non-diy-ai-council/pull/9)

### blog-to-podcast-pipeline

```
Input:    blog post URL or markdown
Output:   polished MP3 podcast with two AI hosts
Cost:     ~$0.50/episode (gpt-4o-mini script + ElevenLabs 2 voices)
Trigger:  "make a podcast from <URL>", "podcast this", "audio version of"
```

Pipeline: fetch the blog → script with two-host dialogue → render each host's lines through ElevenLabs → mix to MP3 → cover image via DALL-E → push.

### council-image-gen

```
Input:    council message or topic
Output:   PNG cover image (square or vertical)
Cost:     ~$0.04/image via DALL-E 3 or ~$0.01 via Flux
Trigger:  "generate an image of X", "cover art for Y", "draw"
```

### media-download

```
Input:    URL from any of 1500+ supported platforms
          (YouTube, Instagram, TikTok, LinkedIn, etc.)
Output:   MP4 in chat + saved to ~/Downloads
Cost:     $0 (yt-dlp under the hood)
Trigger:  "download this", "save the video", a video URL alone
```

## Knowledge & document work

### pdf-publisher

```
Input:    Markdown file or folder
Output:   typeset PDF book / paper / slides
Cost:     $0 (Quarkdown — open-source typesetting on top of Markdown)
Trigger:  "publish PDF", "compile to PDF", "typeset this"
```

Uses [Quarkdown](https://github.com/iamgio/quarkdown) — a Turing-complete typesetting layer over CommonMark. Single .md or .qd source → reveal.js slides, paged.js books, sidebar wikis, plain HTML, all renderable to PDF.

→ Reference: [`agentic-ai-research/dr-non-diy-ai-council` PR #7](https://github.com/agentic-ai-research/dr-non-diy-ai-council/pull/7)

### epub-publisher

```
Input:    Markdown chapters
Output:   Apple-Books-grade EPUB
Cost:     $0
Trigger:  "publish EPUB", "make an ebook", "Kindle this"
```

### tradingagents

```
Input:    Stock ticker (Thai SET or US)
Output:   Multi-agent financial analysis report
Cost:     varies (uses delegated LLM calls per agent)
Trigger:  "analyse stock X", "Thai SET report"
```

→ Reference: [`agentic-ai-research/dr-non-diy-ai-council` PR #8](https://github.com/agentic-ai-research/dr-non-diy-ai-council/pull/8)

## Personal data ops

### card-to-google-contact

```
Input:    photo of a business card (sent to Otto in Telegram)
Output:   contact entry in Google Contacts (both Dr Non's accounts)
Cost:     $0 (uses Google Vision OCR free tier + Contacts API)
Trigger:  "OCR this card", "save contact", or just sending a card photo
```

### gdrive-save

```
Input:    any file in chat OR a URL OR an idea ("save my notes from today")
Output:   file in Google Drive with metadata + folder placement
Cost:     $0 (Drive API)
Trigger:  "save to Drive", "back this up", a file with ambiguous intent
```

### gmail-send

```
Input:    "send email to <recipient> about <topic>"
Output:   draft created in Gmail (NEVER auto-sent — you confirm)
Cost:     $0 (Gmail API)
Trigger:  "send email to X", "draft an email about"
```

### tripit-watcher (daemon)

```
Trigger:  watches your TripIt account every 5 min
Action:   when a new flight is booked, creates Google Calendar entry,
          shares with travel companions, posts notification
Cost:     $0
```

## Council infrastructure

### council-transcript-to-podcast

```
Input:    transcript from a council session
Output:   "Council Live" podcast episode — voiced by Dr Non + co-host
Cost:     ~$0.50/episode
Trigger:  "podcast last night's council", "make this debate listenable"
```

### council-image-gen (covers)

Each daily council retrospective gets a generated cover image. Daemon-driven; runs at midnight Bangkok time on the prior day's session.

### council-retrospective (daemon)

```
Trigger:  daily at 23:55 Bangkok time
Action:   reads the day's council messages, extracts decisions,
          drafts a retrospective summary, posts to a private channel
Cost:     ~$0.10/day
```

### council-health (daemon)

```
Trigger:  every 10 minutes
Action:   pings each bot's gateway, alerts if any are unresponsive
          for >5 minutes; auto-restarts via launchd
Cost:     $0
```

## How a skill gets invoked

When you message *"make a podcast about waiting"*:

1. Tenet sees the message, classifies as TASK MODE, routes to Otto.
2. Otto reads his skill registry, finds `council-transcript-to-podcast` matches "podcast" + content topic.
3. Otto posts: *"Generating podcast on waiting…"* (one line, no preamble).
4. Otto invokes the skill in a subprocess. The skill runs gpt-4o-mini for the script, ElevenLabs for two voices, ffmpeg for mix, DALL-E for cover.
5. When done (typically 60-90 sec), Otto posts the MP3 + cover to chat.
6. The thinkers (in parallel, since they don't block on Otto) post their CONTENT — Bob's Freudian take on waiting, Ana's Kantian duty, Civic's utility argument.
7. Tenet pins the resulting episode + the lens summaries.

The whole thing — deliberation + artefact — takes about 2 minutes.

## Building your own skill

The skill format is intentionally simple. Two files:

```
~/.openclaw/skills/your-skill/
├── SKILL.md                # the manifest — name, description, triggers
└── scripts/
    └── build.py            # the implementation — single file ideally
```

Copy [`tiktok-wisdom`](https://github.com/agentic-ai-research/dr-non-diy-ai-council/tree/main/examples/openclaw/skills/tiktok-wisdom) as a starting template. It demonstrates:

- TOML config files for non-CLI users
- Stage cache for idempotent re-runs
- Multi-provider voice selection (free `mac-say` → paid options)
- HTML preview before committing to TTS
- Pytest unit suite + GitHub Actions CI

→ Next: [`09-failure-modes.md`](09-failure-modes.md) — what goes wrong, how to fix it.
