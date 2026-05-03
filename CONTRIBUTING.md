# Contributing

Contributions are welcome, especially in these areas:

- better PDF table extraction
- OCR support
- Windows/Linux TTS backends
- image occlusion workflows
- richer card mode classifiers
- more APKG compatibility tests

## Development Checks

Run syntax checks:

```bash
python3 -m py_compile scripts/*.py
```

Build and validate the sample deck:

```bash
python3 scripts/build_apkg.py \
  --cards examples/cards.sample.json \
  --out example.apkg \
  --deck-name "Example Deck"

python3 scripts/validate_apkg.py example.apkg
```

Do not commit generated `.apkg`, `.anki2`, `.anki21`, extracted PDF JSON, or audio output.
