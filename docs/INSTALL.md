# Installation

This repository can be used as plain scripts or installed as an AI-agent skill.

## Claude Code

Install as a personal Claude Code skill:

```bash
mkdir -p ~/.claude/skills
cp -R pdf-to-anki-cards ~/.claude/skills/pdf-to-anki-cards
```

Restart Claude Code if it was already running. Then invoke:

```text
/pdf-to-anki-cards
```

or ask naturally:

```text
Use pdf-to-anki-cards to convert this PDF into an Anki deck.
```

## Codex

Install as a personal Codex skill:

```bash
mkdir -p ~/.codex/skills
cp -R pdf-to-anki-cards ~/.codex/skills/pdf-to-anki-cards
```

Restart Codex or start a new session so the skill list refreshes.

## Python Dependencies

Most APKG scripts use only the Python standard library. PDF extraction needs PyMuPDF:

```bash
python3 -m pip install -r requirements.txt
```

## Optional Audio Backends

The skill is designed to avoid hard-coding a single operating system.

- `none`: no audio.
- `reuse`: copy existing media from a reference `.apkg`.
- `anki-tts`: use Anki-native TTS syntax.
- `macos-say`: generate `.aiff` files with macOS `say`.
- `windows-sapi`: planned backend.
- `linux-tts`: planned backend.
- `online-tts`: planned backend that should require explicit API/network approval.
