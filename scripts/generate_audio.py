#!/usr/bin/env python3
import argparse
import json
import platform
import re
import subprocess
from pathlib import Path


def read_cards(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    cards = raw.get("cards", raw) if isinstance(raw, dict) else raw
    if not isinstance(cards, list):
        raise SystemExit("cards JSON must be a list or object with cards")
    return raw, cards


def write_cards(path, raw, cards):
    if isinstance(raw, dict):
        raw["cards"] = cards
        data = raw
    else:
        data = cards
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_name(text):
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")
    return base[:80] or "audio"


def macos_say(cards, out_dir, voice):
    if platform.system() != "Darwin":
        raise SystemExit("macos-say backend requires macOS")
    out_dir.mkdir(parents=True, exist_ok=True)
    for idx, card in enumerate(cards, start=1):
        text = card.get("tts_text") or card.get("word") or card.get("front") or card.get("term")
        if not text or card.get("audio"):
            continue
        name = f"{safe_name(str(text))}-{idx}.aiff"
        path = out_dir / name
        subprocess.run(["say", "-v", voice, "-o", str(path), str(text)], check=True)
        if not path.exists() and Path(str(path) + ".aiff").exists():
            Path(str(path) + ".aiff").rename(path)
        card["audio"] = f"[sound:{name}]"
        card.setdefault("media", []).append({"path": str(path), "name": name, "kind": "audio"})


def anki_tts(cards, lang):
    for card in cards:
        text = card.get("word") or card.get("front") or card.get("term")
        if text and not card.get("audio"):
            card["audio"] = f"{{{{tts {lang}:{text}}}}}"


def main():
    parser = argparse.ArgumentParser(description="Add optional audio fields/media to card JSON.")
    parser.add_argument("--cards", required=True)
    parser.add_argument("--backend", choices=["none", "macos-say", "anki-tts"], default="none")
    parser.add_argument("--out")
    parser.add_argument("--audio-dir", default="audio")
    parser.add_argument("--voice", default="Samantha")
    parser.add_argument("--tts-lang", default="en_US")
    args = parser.parse_args()

    raw, cards = read_cards(args.cards)
    if args.backend == "macos-say":
        macos_say(cards, Path(args.audio_dir), args.voice)
    elif args.backend == "anki-tts":
        anki_tts(cards, args.tts_lang)

    out = args.out or args.cards
    write_cards(out, raw, cards)
    print(f"backend={args.backend} cards={len(cards)} out={out}")


if __name__ == "__main__":
    main()
