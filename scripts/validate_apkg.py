#!/usr/bin/env python3
import argparse
import json
import re
import sqlite3
import tempfile
import zipfile
from pathlib import Path


SOUND_RE = re.compile(r"\[sound:([^\]]+)\]")
IMG_RE = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.I)


def main():
    parser = argparse.ArgumentParser(description="Validate an Anki .apkg package.")
    parser.add_argument("apkg")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    apkg = Path(args.apkg)
    report = {"apkg": str(apkg), "ok": True, "errors": [], "warnings": []}

    try:
        with zipfile.ZipFile(apkg) as zf:
            bad = zf.testzip()
            if bad:
                report["ok"] = False
                report["errors"].append(f"zip member failed CRC: {bad}")
            names = set(zf.namelist())
            report["meta_hex"] = zf.read("meta").hex() if "meta" in names else None
            if "meta" not in names:
                report["warnings"].append("missing meta")
            elif report["meta_hex"] in ("7b7d", ""):
                report["warnings"].append("meta looks like JSON/empty; modern Anki may expect protobuf")

            media = json.loads(zf.read("media").decode("utf-8")) if "media" in names else {}
            report["media_count"] = len(media)
            missing_media_files = [key for key in media if key not in names]
            report["missing_media_files"] = missing_media_files
            if missing_media_files:
                report["ok"] = False
                report["errors"].append(f"{len(missing_media_files)} media keys missing from zip")

            collection = "collection.anki21" if "collection.anki21" in names else "collection.anki2"
            if collection not in names:
                report["ok"] = False
                report["errors"].append("missing collection.anki21/collection.anki2")
            else:
                with tempfile.TemporaryDirectory() as td:
                    zf.extract(collection, td)
                    con = sqlite3.connect(Path(td) / collection)
                    cur = con.cursor()
                    report["notes"] = cur.execute("select count(*) from notes").fetchone()[0]
                    report["cards"] = cur.execute("select count(*) from cards").fetchone()[0]
                    decks = json.loads(cur.execute("select decks from col").fetchone()[0])
                    report["deck_count"] = len(decks)
                    media_values = set(media.values())
                    missing_refs = []
                    referenced = set()
                    for (flds,) in cur.execute("select flds from notes"):
                        for ref in SOUND_RE.findall(flds) + IMG_RE.findall(flds):
                            referenced.add(ref)
                            if ref not in media_values:
                                missing_refs.append(ref)
                    report["referenced_media_count"] = len(referenced)
                    report["missing_media_refs"] = sorted(set(missing_refs))
                    if missing_refs:
                        report["ok"] = False
                        report["errors"].append(f"{len(set(missing_refs))} field media refs missing from media map")
    except Exception as exc:
        report["ok"] = False
        report["errors"].append(str(exc))

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "OK" if report["ok"] else "FAILED"
        print(f"{status}: {apkg}")
        for key in ("notes", "cards", "deck_count", "media_count", "referenced_media_count", "meta_hex"):
            if key in report:
                print(f"{key}: {report[key]}")
        for warning in report["warnings"]:
            print(f"warning: {warning}")
        for error in report["errors"]:
            print(f"error: {error}")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
