---
name: pdf-to-anki-cards
description: Convert PDFs, scanned study materials, vocabulary lists, lecture notes, textbooks, formulas, and image-heavy references into validated Anki .apkg card packages. Use when asked to make Anki cards/decks from PDF or document content, reuse an existing .apkg as a template, extract vocabulary or knowledge points, generate QA/cloze/term/formula/image cards, handle media/audio, or debug Anki package import errors.
---

# PDF to Anki Cards

## Workflow

Use this skill to turn source material into a real Anki package, not just a CSV. Prefer deterministic scripts for extraction, package creation, and validation.

1. Identify inputs: source PDF(s), optional reference `.apkg`, target deck name, card mode, audio policy, output path.
2. Inspect any reference `.apkg` with `scripts/inspect_apkg.py`; reuse its note model, fields, CSS, templates, media, and `meta` whenever appropriate.
3. Extract PDF content with `scripts/extract_pdf_content.py`; preserve page numbers, headings, tables, and image references.
4. Choose card mode:
   - `vocab`: vocabulary, phrase lists, language cards.
   - `qa`: atomic knowledge question/answer cards.
   - `cloze`: fill-in-the-blank cards for definitions, laws, dates, processes.
   - `term`: term-to-definition cards for medicine, law, science, humanities, and technical subjects.
   - `formula`: formulas, theorems, units, derivations.
   - `image`: image-backed cards; image occlusion can be added manually or by future tooling.
5. Build a card JSON file. Keep cards small: one recall target per card. Include `source_page`, `source_text`, `tags`, and `deck_path` when available.
6. Build the `.apkg` with `scripts/build_apkg.py`.
7. Validate the final package with `scripts/validate_apkg.py` before handing it to the user.

## Card Design Rules

- Do not paste full pages into card backs.
- Prefer many small cards over one broad card.
- Make the front prompt answerable from memory without seeing the source.
- Keep the back concise, with optional source context below the answer.
- Use tags/fields for fine-grained organization; reserve decks for broad sections or lessons.
- Preserve source page/section metadata so the user can audit cards later.
- For language decks, include word/phrase, pronunciation, definition, examples, audio, source, and level when available.
- For formulas, preserve symbols, units, assumptions, and a minimal worked cue.
- For image-heavy PDFs, export images as media and reference them from fields; validate every image reference.

## Audio Policy

Do not hard-code macOS audio. Choose an audio backend explicitly:

- `none`: no audio.
- `reuse`: copy existing audio from a reference `.apkg`.
- `anki-tts`: use Anki-native TTS template syntax instead of media files.
- `macos-say`: use macOS `say`; expect `.aiff` output and verify filenames.
- `windows-sapi`: use PowerShell/SAPI where available.
- `linux-tts`: use installed tools such as `espeak-ng` or `piper`.
- `online-tts`: use a network/API backend only after user approval.

For cross-device reliability, real media files plus Anki media sync are most predictable. Anki-native TTS is lighter but client behavior can vary.

## APKG Rules

Read `references/anki-apkg-format.md` before editing low-level package code.

Critical invariants:

- `.apkg` is a zip archive, but the contents are Anki-specific.
- `media` maps zip-internal numeric filenames to user-facing media names.
- Every `[sound:name]` or `<img src="name">` reference in note fields must appear as a value in `media`.
- Every key in `media` must exist as a file in the zip.
- Do not write `meta` as `{}` for modern packages. Reuse reference-package `meta` when possible; malformed `meta` can cause `ProtoError: buffer underflow`.
- Prefer `collection.anki21` for modern Anki. Include `collection.anki2` only as a conservative compatibility fallback.

## Scripts

- `scripts/inspect_apkg.py <deck.apkg> --out inspect.json`
  Inspect note models, fields, templates, decks, note counts, media counts, and `meta` bytes.

- `scripts/extract_pdf_content.py <source.pdf> --out content.json`
  Extract page text and a best-effort vocabulary table when the PDF has repeated Word/Meaning columns.

- `scripts/build_apkg.py --cards cards.json --out deck.apkg [--reference template.apkg] [--deck-name NAME]`
  Build a validated Anki package from structured cards. Use a reference package when the user asks for matching style.

- `scripts/generate_audio.py --cards cards.json --backend none|reuse|macos-say|anki-tts`
  Prepare audio metadata or generated audio. Platform-specific backends must degrade gracefully.

- `scripts/validate_apkg.py deck.apkg`
  Validate zip integrity, SQLite note/card counts, media mappings, and sound/image references.

## Output Expectations

Return the final `.apkg` path, summarize counts, and report validation results:

- note count
- card count
- deck count
- media count
- missing media references
- any skipped or low-confidence extraction areas

If validation fails, fix the package before final delivery unless the failure is caused by an unavailable user-provided file or missing external dependency.
