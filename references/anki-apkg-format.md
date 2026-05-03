# Anki APKG Format Notes

Use this reference before building or repairing an `.apkg`.

## Package Layout

An `.apkg` is a zip archive. A modern package commonly contains:

- `meta`: protobuf bytes. Do not replace with `{}` unless you know the target Anki version expects JSON.
- `collection.anki21`: modern SQLite collection database.
- `collection.anki2`: legacy compatibility database or fallback.
- `media`: JSON object mapping zip-internal numeric filenames to media filenames used in note fields.
- numeric media files: `0`, `1`, `2`, ...

## Media Mapping

The `media` file looks like:

```json
{
  "0": "audio_name_initial.svg",
  "1": "word.mp3",
  "2": "diagram.png"
}
```

The zip must contain files named `0`, `1`, `2`. Note fields must refer to values:

```html
[sound:word.mp3]
<img src="diagram.png">
```

Validation must check both directions:

- every media key exists in the zip
- every `[sound:...]` or `<img src="...">` reference exists among media values

## SQLite Tables

The build scripts mainly need:

- `col`: global collection metadata, note models, decks, deck configs.
- `notes`: note rows; fields are joined with ASCII unit separator `\x1f`.
- `cards`: generated cards.
- `revlog` and `graves`: usually clear these for new generated decks.

When reusing a reference deck, copy its `collection.anki21`, then clear `notes`, `cards`, `revlog`, and `graves` before inserting new notes.

## Meta Pitfall

Modern Anki may decode `meta` as protobuf. If `meta` is malformed, import can fail with:

```text
ProtoError { info: "failed to decode Protobuf message: buffer underflow" }
```

Conservative rule: when a reference `.apkg` is provided, reuse its `meta` exactly. When no reference exists, write protobuf bytes `08 02` for a modern package and validate in Anki if possible.

## IDs and Checksums

Use stable but unique values:

- note `guid`: deterministic base64-ish hash of deck/card content
- note/card ids: timestamp-like integers
- note `csum`: first 8 hex digits of SHA1 of sort field, interpreted as integer
- card `did`: target deck id

Do not reuse source deck review history unless explicitly asked.
