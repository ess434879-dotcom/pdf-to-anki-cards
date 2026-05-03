# Card Design Rules

## General

- One card should ask for one thing.
- Prefer active recall: the front should be a prompt, not a heading.
- The back should answer the prompt first, then provide context.
- Keep source page, chapter, and original phrase as metadata.
- Use tags for topic, source, difficulty, chapter, and extraction confidence.

## QA Cards

Good:

```text
Front: Why does increasing temperature usually increase reaction rate?
Back: Particles collide more frequently and with higher energy, so more collisions exceed activation energy.
```

Avoid:

```text
Front: Reaction rates
Back: A full paragraph copied from the textbook.
```

## Cloze Cards

Use cloze for facts with a missing key term, date, number, cause, or condition.

```text
The sinoatrial node is the heart's primary {{c1::pacemaker}}.
```

If the builder does not create native Anki cloze notes, convert cloze text to a front/back card where the front contains the blank and the back contains the filled statement.

## Term Cards

Use for definitions:

```text
Front: osmotic pressure
Back: Pressure required to prevent solvent flow through a semipermeable membrane.
```

## Formula Cards

Include formula, variables, units, and a recall cue.

```text
Front: What is Newton's second law?
Back: F = ma. F is net force, m is mass, a is acceleration.
```

## Vocabulary Cards

Include as many fields as are available:

- word or phrase
- pronunciation
- concise definition
- detailed definition
- example sentence
- translation
- word forms
- audio
- source page or lesson
- level or tags

Do not hallucinate examples when the source or dictionary is unavailable; leave optional fields empty or mark low confidence.
