# Content Modes

## auto

Inspect page text and headings, then choose the dominant mode. Use `vocab` for repeated word/meaning tables. Use `term` for glossary-like material. Use `qa` for prose lessons. Use `formula` for formula-heavy pages. Use `image` for pages dominated by diagrams.

## vocab

Best for language decks and word lists. Expected source patterns:

- Word / Meaning columns
- term followed by definition
- numbered word lists
- bilingual tables

Card fields should include `word`, `definition`, `phonetic`, `example`, `audio`, `source_page`, and tags.

## qa

Best for textbook and lecture prose. Extract atomic facts and relationships. Generate concise front/back cards.

## cloze

Best for exact facts:

- dates
- laws
- terminology
- enumerations
- definitions
- cause/effect statements

## term

Best for glossary, medicine, law, science, and technical definitions.

## formula

Best for math, physics, chemistry, statistics, and engineering PDFs. Preserve notation. If OCR distorts formulas, flag for review instead of guessing.

## image

Best for diagrams, maps, anatomy, circuits, charts, or workflows. Extract images and create cards with source prompt and image media. True image occlusion can be a future extension.
