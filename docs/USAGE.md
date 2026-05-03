# Usage

## 1. Inspect a Reference Deck

```bash
python3 scripts/inspect_apkg.py reference.apkg --out inspect.json
```

This reports:

- note model names
- field names
- templates
- deck names
- note/card counts
- media count
- `meta` bytes

## 2. Extract PDF Content

```bash
python3 scripts/extract_pdf_content.py source.pdf --out extracted.json
```

For vocabulary-style PDFs with repeated `Word` / `Meaning` columns:

```bash
python3 scripts/extract_pdf_content.py source.pdf --mode vocab --out extracted.json
```

The output includes:

- `pages`: page text and image count
- `vocab`: best-effort extracted word/definition rows

## 3. Build a Basic Deck

```bash
python3 scripts/build_apkg.py \
  --cards examples/cards.sample.json \
  --out example.apkg \
  --deck-name "Example Deck"
```

## 4. Build with a Reference Deck

```bash
python3 scripts/build_apkg.py \
  --cards cards.json \
  --reference reference.apkg \
  --out generated.apkg \
  --deck-name "Generated Deck"
```

This reuses the reference package's model/template/CSS and preserves safe APKG metadata.

## 5. Add macOS TTS Audio

```bash
python3 scripts/generate_audio.py \
  --cards cards.json \
  --backend macos-say \
  --audio-dir generated-audio \
  --out cards.with-audio.json
```

Then build from `cards.with-audio.json`.

## 6. Validate Before Import

```bash
python3 scripts/validate_apkg.py generated.apkg
```

A healthy result looks like:

```text
OK: generated.apkg
notes: 2
cards: 2
deck_count: 1
media_count: 0
meta_hex: 0802
```

## Card JSON Fields

Common fields:

| Field | Purpose |
| --- | --- |
| `type` | `qa`, `vocab`, `term`, `cloze`, `formula`, or `image` |
| `front` | Front-side prompt |
| `back` | Back-side answer |
| `word` | Vocabulary word |
| `term` | Term for definition cards |
| `definition` | Definition or meaning |
| `source_page` | Page number from source PDF |
| `source_text` | Short source excerpt |
| `deck_path` | Optional subdeck name |
| `tags` | List of Anki tags |
| `audio` | `[sound:file]` or Anki TTS syntax |
| `image` | `<img src="file.png">` |
| `media` | List of media files to include |

Media item example:

```json
{
  "path": "assets/aggressive.aiff",
  "name": "aggressive.aiff",
  "kind": "audio"
}
```
