#!/usr/bin/env python3
import argparse
import json
import sqlite3
import tempfile
import zipfile
from pathlib import Path


def read_json_member(zf, name, default):
    try:
        return json.loads(zf.read(name).decode("utf-8"))
    except Exception:
        return default


def main():
    parser = argparse.ArgumentParser(description="Inspect an Anki .apkg package.")
    parser.add_argument("apkg")
    parser.add_argument("--out")
    args = parser.parse_args()

    apkg = Path(args.apkg)
    result = {"apkg": str(apkg), "ok": True}

    with zipfile.ZipFile(apkg) as zf:
        names = set(zf.namelist())
        result["members"] = sorted(names)[:20]
        result["member_count"] = len(names)
        result["meta_hex"] = zf.read("meta").hex() if "meta" in names else None
        result["media"] = read_json_member(zf, "media", {})
        result["media_count"] = len(result["media"])

        collection_name = "collection.anki21" if "collection.anki21" in names else "collection.anki2"
        result["collection"] = collection_name if collection_name in names else None
        if result["collection"] is None:
            result["ok"] = False
            result["error"] = "No collection.anki21 or collection.anki2 found."
        else:
            with tempfile.TemporaryDirectory() as td:
                zf.extract(collection_name, td)
                db = Path(td) / collection_name
                con = sqlite3.connect(db)
                cur = con.cursor()
                result["notes"] = cur.execute("select count(*) from notes").fetchone()[0]
                result["cards"] = cur.execute("select count(*) from cards").fetchone()[0]
                col = cur.execute("select models, decks from col").fetchone()
                models = json.loads(col[0])
                decks = json.loads(col[1])
                result["models"] = [
                    {
                        "id": mid,
                        "name": model.get("name"),
                        "fields": [f.get("name") for f in model.get("flds", [])],
                        "templates": [t.get("name") for t in model.get("tmpls", [])],
                    }
                    for mid, model in models.items()
                ]
                result["deck_count"] = len(decks)
                result["decks"] = [deck.get("name") for deck in decks.values()][:50]

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
