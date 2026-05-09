# Diagrams (Mermaid version)

GitHub-rendered Mermaid versions of the six SVG diagrams in [`../diagrams/`](../diagrams/). Use whichever shape works best for your reader — the SVGs are sharper and image-friendly; the Mermaid blocks below are inspectable + editable in-line.

## 1. System map

```mermaid
flowchart LR
  U["Dr Non\nNatural-language command"] --> TG["Telegram group chat\nFree platform-as-a-service\nworking memory + audit trail"]

  TG --> Tenet["Tenet\nChair / Devil's Advocate\nRoutes + synthesises"]
  TG --> Thinkers["Reasoners\nAna · Civic · Hannah · Bob · Pip · noN\nEach adds one locked lens"]
  Thinkers --> Tenet
  Tenet -->|DEBATE| Thinkers
  Tenet -->|ACTION / RENDERING| Otto["Otto\nExecutor\nRuns skills + ships artefacts"]
  Otto --> TG
  TG --> Radar["Radar\nSecretary / Scribe"]
  Radar --> Brain["Obsidian Brain\nLong-term memory\nsessions + artefacts"]
  Brain --> Radar

  Soul["SOUL markdown files\nidentity · lens · task routing\nanti-duplicate · output format"] --> Tenet
  Soul --> Thinkers
  Providers["LLM providers\nOpenRouter · Gemini · Qwen\nMistral · Groq · NVIDIA"] --> Tenet
  Providers --> Thinkers
  Providers --> Otto
  Providers --> Radar
  Tools["Tools + skills\nOCR · PDF · podcast · Drive · email · media"] --> Otto
```

## 2. One council turn

```mermaid
flowchart LR
  A["1. Inbound\nDr Non posts in Telegram"] --> B["2. Awaken\nEach bot gateway receives the message"]
  B --> C["3. Contribute\nOnly useful lenses speak\nOne message per bot per turn"]
  C --> D{"4. Tenet routes\nDebate or task?"}
  D -->|CONTENT / JUDGMENT| E["5A. Debate\nThinkers expand, qualify, concede, stand, or pass"]
  D -->|ACTION / RENDERING| F["5B. Execute\nOtto runs the relevant skill"]
  E --> G["6. Synthesis\nTenet pins decision or names open question"]
  F --> G
  G --> H["7. Scribe\nRadar writes the session to Obsidian"]
```

## 3. The council roles

```mermaid
flowchart TB
  Tenet["Tenet\nChair + Devil's Advocate\nFirst principles + systems"]

  Ana["Ana\nDuty + pragmatism\nKant / James"] --> Tenet
  Civic["Civic\nConsequences + unconscious drives\nMill / Freud / Lewis"] --> Tenet
  Hannah["Hannah\nPattern + category error\nDouglas / Malinowski / Tversky"] --> Tenet
  Bob["Bob\nThe unsaid + ground sense\nFreud + common sense"] --> Tenet
  Pip["Pip\nDesign craft\nRams / Vignelli"] --> Tenet
  noN["noN\nShadow lens\nJung"] --> Tenet

  Tenet -->|task| Otto["Otto\nExecutor\nSkills + tools"]
  Tenet -->|decision| Radar["Radar\nSecretary\nSession log + memory"]
  Radar -->|recall| Tenet
```

## 4. Engine ladder

```mermaid
flowchart LR
  Pico["picoclaw\nTiny\nOne job · no tools"] --> Nano["nanobot\nSmall\nOne bot · light tools\nCouncil workhorse"]
  Nano --> Open["openclaw\nMedium\nSkill runner\nOtto heavy work"]
  Open --> Hermes["hermes\nLarge\nFull assistant\nRadar + memory + daemons"]

  Rule["Rule: pick the smallest engine that does the job.\nDo not run Hermes when Picoclaw will do."]
  Hermes --> Rule
```

## 5. CONTENT vs ACTION routing

```mermaid
flowchart TB
  Q["Incoming request"] --> D1{"Need a real artefact?\nemail · OCR · file · MP3 · PNG · Drive"}
  D1 -->|yes| A["ACTION / RENDERING\nOtto owns execution"]
  D1 -->|no| D2{"Is there substance to think about?\ntopic · ethics · framing · design · strategy"}
  A --> D2
  D2 -->|yes| C["CONTENT / JUDGMENT\nReasoners give lensed takes"]
  D2 -->|no| P["PASS\nOnly legitimate when pure rendering\nand no content question exists"]
  C --> S["Tenet synthesises\nRadar logs"]
  A --> S
  P --> S
```

## 6. Memory and artefact flow

```mermaid
flowchart LR
  TG["Telegram chat\nWorking memory\nfast · visible · auditable"] --> PIN["Pinned decision\nTenet synthesis"]
  TG --> RAD["Radar daemon\nwatches + summarizes"]
  RAD --> CO["~/Brain/Council/sessions/\ntranscripts + decisions"]
  RAD --> OO["OccipitalLobe\nvisual artefacts\ndiagrams · screenshots · videos"]
  RAD --> TT["TemporalLobe\nsemantic artefacts\npodcasts · writings · corpus"]
  RAD --> HH["Hippocampus\nepisodes + people\nwho / what / when"]
  CO --> RE["Future query\nWhat did we decide?"]
  OO --> RE
  TT --> RE
  HH --> RE
  RE --> TG
```
