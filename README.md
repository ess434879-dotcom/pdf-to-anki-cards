# PDF to Anki Cards

[English](README.en.md) | [简体中文](README.zh-CN.md)

Convert PDFs, vocabulary lists, lecture notes, textbook pages, formulas, and image-heavy study materials into validated Anki `.apkg` packages.

This repository packages a reusable AI-agent skill plus deterministic helper scripts. It grew out of a real PDF-to-Anki workflow where preserving Anki package details mattered: note models, templates, media mappings, and the protobuf `meta` file all need to be handled carefully for smooth import.

## Repository Description

**PDF to Anki Cards** is a Claude Code/Codex skill and Python toolkit for turning PDF study materials into import-ready Anki decks. It combines agent-guided card generation with deterministic `.apkg` building and validation scripts, so generated cards can preserve templates, media, audio, and Anki package metadata reliably.

This project is a full-on vibe coding project: the initial workflow, implementation, documentation, and repository packaging were produced through human-directed AI coding sessions.

## What It Does

- Extracts text and vocabulary tables from PDFs.
- Builds Anki `.apkg` files from structured card JSON.
- Reuses an existing `.apkg` as a style/template source.
- Preserves Anki media mappings for audio and images.
- Validates package integrity before import.
- Supports multiple card modes: vocabulary, QA, cloze-style, terms, formulas, and image-backed cards.
- Includes a Claude Code / Codex compatible `SKILL.md`.

## Repository Layout

```text
.
├── SKILL.md                         # Agent skill instructions
├── package.json                     # npm/npx install metadata
├── bin/
│   └── pdf-to-anki-cards.js         # npm installer CLI
├── scripts/
│   ├── inspect_apkg.py              # Inspect reference Anki packages
│   ├── extract_pdf_content.py       # Extract text and vocab tables from PDFs
│   ├── build_apkg.py                # Build .apkg from structured card JSON
│   ├── generate_audio.py            # Optional audio metadata/generation helper
│   └── validate_apkg.py             # Validate final .apkg files
├── references/
│   ├── anki-apkg-format.md          # APKG implementation notes
│   ├── card-design-rules.md         # Good flashcard design rules
│   └── content-modes.md             # Supported content modes
├── docs/
│   ├── INSTALL.md                   # Install as Claude Code/Codex skill
│   ├── INSTALL.zh-CN.md             # Chinese installation guide
│   └── USAGE.md                     # Command examples
└── examples/
    └── cards.sample.json            # Minimal card JSON example
```

## Quick Start

Install as an agent skill with npm/npx:

```bash
npx github:ess434879-dotcom/pdf-to-anki-cards install --target claude
```

or install globally from GitHub:

```bash
npm install -g github:ess434879-dotcom/pdf-to-anki-cards
pdf-to-anki-cards install --target claude
```

See [docs/INSTALL.md](docs/INSTALL.md) for Claude Code, Codex, Git, and npm installation options.

Create a tiny example deck:

```bash
python3 scripts/build_apkg.py \
  --cards examples/cards.sample.json \
  --out example.apkg \
  --deck-name "Example PDF Cards"

python3 scripts/validate_apkg.py example.apkg
```

Inspect an existing Anki package:

```bash
python3 scripts/inspect_apkg.py path/to/reference.apkg --out inspect.json
```

Extract a PDF:

```bash
python3 scripts/extract_pdf_content.py path/to/source.pdf --out extracted.json
```

`extract_pdf_content.py` requires PyMuPDF:

```bash
python3 -m pip install -r requirements.txt
```

## Card JSON Format

The builder accepts either a list of cards or an object with a `cards` list.

```json
[
  {
    "type": "qa",
    "front": "What is active recall?",
    "back": "A study method where you retrieve the answer from memory before checking it.",
    "source_page": 1,
    "tags": ["study", "memory"]
  }
]
```

For vocabulary cards:

```json
{
  "type": "vocab",
  "word": "aggressive",
  "definition": "adj. 好斗的，有侵略性的；进取的",
  "phonetic": "/əˈɡresɪv/",
  "audio": "[sound:aggressive.mp3]",
  "source_page": 1,
  "tags": ["cet6", "vocab"]
}
```

## Reference Decks

When a reference `.apkg` is provided, `build_apkg.py` reuses its note model, templates, CSS, and `meta` bytes:

```bash
python3 scripts/build_apkg.py \
  --cards cards.json \
  --reference reference.apkg \
  --out generated.apkg \
  --deck-name "Generated Deck"
```

This is useful when you want a new deck to look and behave like an existing deck.

## Why Validation Matters

Anki packages are zip files, but they are not just arbitrary zip files. Common mistakes cause import errors or missing media:

- malformed `meta` file
- `[sound:...]` references missing from `media`
- `media` keys missing from the zip
- mismatched note/card counts

Always run:

```bash
python3 scripts/validate_apkg.py generated.apkg
```

## Agent Skill Usage

Install this repository as a Claude Code or Codex skill, then ask:

```text
Use pdf-to-anki-cards to convert this PDF into an Anki deck.
```

See [docs/INSTALL.md](docs/INSTALL.md).

## Status

This is an early practical toolkit. The APKG build/validate path is deterministic and tested on small decks and a real vocabulary PDF workflow. PDF-to-card reasoning still depends on the calling agent for high-quality QA/cloze generation.

## License

MIT License. See [LICENSE](LICENSE).
