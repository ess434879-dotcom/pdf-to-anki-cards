#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
import os
import re
import shutil
import sqlite3
import tempfile
import time
import zipfile
from pathlib import Path


FIELD_SEP = "\x1f"
SOUND_RE = re.compile(r"\[sound:([^\]]+)\]")
IMG_RE = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.I)


def now_s():
    return int(time.time())


def checksum(text):
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16)


def guid(text):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-"
    n = int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:16], 16)
    out = ""
    while n:
        n, r = divmod(n, len(alphabet))
        out += alphabet[r]
    return out or "0"


def read_cards(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    cards = raw.get("cards", raw) if isinstance(raw, dict) else raw
    if not isinstance(cards, list):
        raise SystemExit("cards JSON must be a list or an object with a cards list")
    return cards


def clean(value):
    if value is None:
        return ""
    return str(value)


def html_text(value):
    return html.escape(clean(value)).replace("\n", "<br>")


def card_front(card):
    return clean(
        card.get("front")
        or card.get("question")
        or card.get("prompt")
        or card.get("word")
        or card.get("term")
        or card.get("title")
    )


def card_back(card):
    return clean(
        card.get("back")
        or card.get("answer")
        or card.get("definition")
        or card.get("meaning")
        or card.get("explanation")
    )


def card_source(card):
    parts = []
    if card.get("source_page"):
        parts.append(f"page {card['source_page']}")
    if card.get("source_section"):
        parts.append(str(card["source_section"]))
    if card.get("source_text"):
        parts.append(str(card["source_text"]))
    return "<br>".join(html_text(part) for part in parts)


def card_tags(card):
    tags = card.get("tags", [])
    if isinstance(tags, str):
        tags = re.split(r"\s+", tags.strip())
    return " " + " ".join(t.replace(" ", "_") for t in tags if t) + " "


def collect_refs_from_fields(fields):
    refs = set()
    for value in fields:
        refs.update(SOUND_RE.findall(value))
        refs.update(IMG_RE.findall(value))
    return refs


def default_model(model_id):
    fields = ["CardType", "Front", "Back", "Source", "Extra", "Audio", "Image"]
    return {
        str(model_id): {
            "id": model_id,
            "name": "PDF to Anki Cards Basic",
            "type": 0,
            "mod": now_s(),
            "usn": -1,
            "sortf": 1,
            "did": None,
            "tmpls": [
                {
                    "name": "Card 1",
                    "ord": 0,
                    "qfmt": '<div class="card-type">{{CardType}}</div><div class="front">{{Front}}</div>{{#Image}}<div class="image">{{Image}}</div>{{/Image}}{{Audio}}',
                    "afmt": '{{FrontSide}}<hr id="answer"><div class="back">{{Back}}</div>{{#Source}}<div class="source">{{Source}}</div>{{/Source}}{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}',
                    "bqfmt": "",
                    "bafmt": "",
                    "did": None,
                    "bfont": "",
                    "bsize": 0,
                }
            ],
            "flds": [
                {
                    "name": name,
                    "ord": i,
                    "sticky": False,
                    "rtl": False,
                    "font": "Arial",
                    "size": 20,
                    "description": "",
                    "plainText": False,
                    "collapsed": False,
                    "excludeFromSearch": False,
                    "tag": None,
                    "preventDeletion": False,
                }
                for i, name in enumerate(fields)
            ],
            "css": """
.card { font-family: Arial, sans-serif; font-size: 20px; text-align: left; color: #111; background: #fff; padding: 24px; line-height: 1.45; }
.front { font-size: 28px; font-weight: 700; margin: 16px 0; }
.back { font-size: 22px; margin: 16px 0; }
.source, .extra, .card-type { color: #666; font-size: 14px; margin-top: 16px; }
img { max-width: 100%; height: auto; }
""",
            "latexPre": "",
            "latexPost": "",
            "latexsvg": False,
            "req": [[0, "any", [1]]],
            "tags": [],
            "vers": [],
        }
    }


def deck_entry(did, name):
    return {
        "id": did,
        "name": name,
        "mod": now_s(),
        "usn": -1,
        "lrnToday": [0, 0],
        "revToday": [0, 0],
        "newToday": [0, 0],
        "timeToday": [0, 0],
        "collapsed": False,
        "browserCollapsed": False,
        "desc": "",
        "dyn": 0,
        "conf": 1,
        "extendNew": 0,
        "extendRev": 0,
    }


def create_empty_db(path, deck_name):
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executescript(
        """
CREATE TABLE col (
  id integer PRIMARY KEY,
  crt integer NOT NULL,
  mod integer NOT NULL,
  scm integer NOT NULL,
  ver integer NOT NULL,
  dty integer NOT NULL,
  usn integer NOT NULL,
  ls integer NOT NULL,
  conf text NOT NULL,
  models text NOT NULL,
  decks text NOT NULL,
  dconf text NOT NULL,
  tags text NOT NULL
);
CREATE TABLE notes (
  id integer PRIMARY KEY,
  guid text NOT NULL,
  mid integer NOT NULL,
  mod integer NOT NULL,
  usn integer NOT NULL,
  tags text NOT NULL,
  flds text NOT NULL,
  sfld integer NOT NULL,
  csum integer NOT NULL,
  flags integer NOT NULL,
  data text NOT NULL
);
CREATE TABLE cards (
  id integer PRIMARY KEY,
  nid integer NOT NULL,
  did integer NOT NULL,
  ord integer NOT NULL,
  mod integer NOT NULL,
  usn integer NOT NULL,
  type integer NOT NULL,
  queue integer NOT NULL,
  due integer NOT NULL,
  ivl integer NOT NULL,
  factor integer NOT NULL,
  reps integer NOT NULL,
  lapses integer NOT NULL,
  left integer NOT NULL,
  odue integer NOT NULL,
  odid integer NOT NULL,
  flags integer NOT NULL,
  data text NOT NULL
);
CREATE TABLE revlog (
  id integer PRIMARY KEY,
  cid integer NOT NULL,
  usn integer NOT NULL,
  ease integer NOT NULL,
  ivl integer NOT NULL,
  lastIvl integer NOT NULL,
  factor integer NOT NULL,
  time integer NOT NULL,
  type integer NOT NULL
);
CREATE TABLE graves (
  usn integer NOT NULL,
  oid integer NOT NULL,
  type integer NOT NULL
);
"""
    )
    model_id = int(time.time() * 1000) % 10_000_000_000
    deck_id = model_id + 1000
    models = default_model(model_id)
    decks = {str(deck_id): deck_entry(deck_id, deck_name)}
    dconf = {"1": {"id": 1, "name": "Default", "mod": now_s(), "usn": -1, "maxTaken": 60, "autoplay": True, "timer": 0}}
    conf = {"nextPos": 1, "schedVer": 2}
    cur.execute(
        "insert into col values (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (1, int(time.time() // 86400), now_s(), now_s() * 1000, 11, 0, -1, 0, json.dumps(conf), json.dumps(models), json.dumps(decks), json.dumps(dconf), "{}"),
    )
    con.commit()
    return con


def prepare_db(reference, build_dir, deck_name):
    meta = bytes.fromhex("0802")
    if reference:
        with zipfile.ZipFile(reference) as zf:
            names = set(zf.namelist())
            collection = "collection.anki21" if "collection.anki21" in names else "collection.anki2"
            zf.extract(collection, build_dir)
            db_path = build_dir / "collection.anki21"
            shutil.move(str(build_dir / collection), db_path)
            if "meta" in names:
                meta = zf.read("meta")
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        for table in ("notes", "cards", "revlog", "graves"):
            cur.execute(f"delete from {table}")
        cur.execute("update col set decks=? where id=1", ("{}",))
        con.commit()
        return con, db_path, meta

    db_path = build_dir / "collection.anki21"
    con = create_empty_db(db_path, deck_name)
    return con, db_path, meta


def choose_model(cur, model_name=None):
    models = json.loads(cur.execute("select models from col").fetchone()[0])
    if model_name:
        for mid, model in models.items():
            if model.get("name") == model_name:
                return int(mid), model
        raise SystemExit(f"model not found: {model_name}")
    mid = next(iter(models.keys()))
    return int(mid), models[mid]


def field_values_for_model(card, field_names):
    aliases = {
        "Word": ["word", "term", "front"],
        "Phonetic": ["phonetic", "pronunciation"],
        "Definition": ["definition", "meaning", "back", "answer"],
        "Audio": ["audio"],
        "Eudic": ["eudic"],
        "MetaInfo": ["meta", "source", "source_page"],
        "NoteField": ["note", "extra"],
        "Level": ["level"],
        "WordForm": ["word_form", "forms"],
        "SimpleDef": ["simple_def", "definition", "back"],
        "ExampleSentence": ["example_sentence", "example"],
        "CardType": ["type"],
        "Front": ["front", "question", "prompt", "word", "term"],
        "Back": ["back", "answer", "definition", "meaning", "explanation"],
        "Source": ["source"],
        "Extra": ["extra", "note"],
        "Image": ["image"],
        "Text": ["text", "cloze", "front"],
    }
    computed = {
        "type": clean(card.get("type", "qa")),
        "front": html_text(card_front(card)),
        "back": html_text(card_back(card)),
        "source": card_source(card),
        "audio": clean(card.get("audio", "")),
        "image": clean(card.get("image", "")),
        "extra": html_text(card.get("extra", "")),
    }
    values = []
    for i, name in enumerate(field_names):
        value = ""
        if name in card:
            value = clean(card[name])
        else:
            for alias in aliases.get(name, []):
                if alias in computed:
                    value = computed[alias]
                    break
                if alias in card:
                    value = clean(card[alias])
                    break
        if not value:
            if i == 0:
                value = computed["front"]
            elif i == 1:
                value = computed["back"]
        values.append(value)
    return values


def ensure_decks(cur, deck_name, cards):
    col = cur.execute("select decks from col").fetchone()
    decks = json.loads(col[0])
    next_id = max([int(k) for k in decks.keys()] + [int(time.time() * 1000)]) + 1
    path_to_id = {d.get("name"): int(did) for did, d in decks.items()}

    if deck_name not in path_to_id:
        did = next_id
        next_id += 1
        decks[str(did)] = deck_entry(did, deck_name)
        path_to_id[deck_name] = did

    card_deck_ids = []
    for card in cards:
        raw = clean(card.get("deck_path") or card.get("deck") or deck_name)
        full = raw if raw == deck_name or raw.startswith(deck_name + "::") else f"{deck_name}::{raw}"
        if full not in path_to_id:
            did = next_id
            next_id += 1
            decks[str(did)] = deck_entry(did, full)
            path_to_id[full] = did
        card_deck_ids.append(path_to_id[full])

    cur.execute("update col set decks=?, mod=?, scm=? where id=1", (json.dumps(decks, ensure_ascii=False), now_s(), now_s() * 1000))
    return card_deck_ids


def add_media_file(media, media_dir, source_path, desired_name=None):
    source = Path(source_path)
    if not source.exists():
        raise SystemExit(f"media file not found: {source}")
    name = desired_name or source.name
    if name in media.values():
        return name
    key = str(len(media))
    shutil.copy2(source, media_dir / key)
    media[key] = name
    return name


def seed_reference_media(reference, media, media_dir, needed_names):
    if not reference:
        return
    with zipfile.ZipFile(reference) as zf:
        ref_media = json.loads(zf.read("media").decode("utf-8")) if "media" in zf.namelist() else {}
        by_name = {v: k for k, v in ref_media.items()}
        for name, key in by_name.items():
            if name in needed_names or name.lower().endswith((".svg", ".css")):
                if name in media.values() or key not in zf.namelist():
                    continue
                out_key = str(len(media))
                (media_dir / out_key).write_bytes(zf.read(key))
                media[out_key] = name


def package_apkg(out, build_dir, db_path, meta, media):
    (build_dir / "meta").write_bytes(meta)
    (build_dir / "media").write_text(json.dumps(media, ensure_ascii=False), encoding="utf-8")
    shutil.copy2(db_path, build_dir / "collection.anki2")
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w") as zf:
        zf.write(build_dir / "meta", "meta", compress_type=zipfile.ZIP_STORED)
        zf.write(db_path, "collection.anki21", compress_type=zipfile.ZIP_DEFLATED)
        zf.write(build_dir / "collection.anki2", "collection.anki2", compress_type=zipfile.ZIP_STORED)
        zf.write(build_dir / "media", "media", compress_type=zipfile.ZIP_STORED)
        media_dir = build_dir / "media_files"
        for key in media:
            zf.write(media_dir / key, key, compress_type=zipfile.ZIP_STORED)


def main():
    parser = argparse.ArgumentParser(description="Build an Anki .apkg from structured card JSON.")
    parser.add_argument("--cards", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--reference")
    parser.add_argument("--deck-name", default="PDF to Anki Cards")
    parser.add_argument("--model-name")
    parser.add_argument("--workdir")
    args = parser.parse_args()

    cards = read_cards(args.cards)
    out = Path(args.out)
    work_parent = Path(args.workdir) if args.workdir else Path(tempfile.mkdtemp(prefix="pdf-to-anki-"))
    build_dir = work_parent / "build"
    media_dir = build_dir / "media_files"
    media_dir.mkdir(parents=True, exist_ok=True)

    con, db_path, meta = prepare_db(args.reference, build_dir, args.deck_name)
    cur = con.cursor()
    mid, model = choose_model(cur, args.model_name)
    field_names = [field["name"] for field in model.get("flds", [])]
    deck_ids = ensure_decks(cur, args.deck_name, cards)

    media = {}
    needed_media = set()
    all_fields = []
    rows = []
    base_id = int(time.time() * 1000)
    for idx, card in enumerate(cards, start=1):
        fields = field_values_for_model(card, field_names)
        for item in card.get("media", []) if isinstance(card.get("media", []), list) else []:
            name = add_media_file(media, media_dir, item["path"], item.get("name"))
            if item.get("kind") == "audio" and "Audio" in field_names and not fields[field_names.index("Audio")]:
                fields[field_names.index("Audio")] = f"[sound:{name}]"
            if item.get("kind") == "image" and "Image" in field_names and not fields[field_names.index("Image")]:
                fields[field_names.index("Image")] = f'<img src="{html.escape(name)}">'
        needed_media.update(collect_refs_from_fields(fields))
        all_fields.append(fields)
        sort_field = re.sub(r"<[^>]+>", "", fields[0]) if fields else f"card {idx}"
        nid = base_id + idx * 2
        cid = nid + 1
        rows.append((nid, cid, deck_ids[idx - 1], sort_field, fields, card_tags(card)))

    seed_reference_media(args.reference, media, media_dir, needed_media)

    for idx, (nid, cid, did, sort_field, fields, tags) in enumerate(rows, start=1):
        cur.execute(
            "insert into notes values (?,?,?,?,?,?,?,?,?,?,?)",
            (
                nid,
                guid(f"{args.deck_name}:{sort_field}:{idx}"),
                mid,
                now_s(),
                -1,
                tags,
                FIELD_SEP.join(fields),
                sort_field,
                checksum(sort_field),
                0,
                "",
            ),
        )
        cur.execute(
            "insert into cards values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (cid, nid, did, 0, now_s(), -1, 0, 0, idx, 0, 0, 0, 0, 0, 0, 0, 0, "{}"),
        )
    con.commit()
    con.close()

    package_apkg(out, build_dir, db_path, meta, media)
    print(f"created={out}")
    print(f"cards={len(cards)} media={len(media)}")


if __name__ == "__main__":
    main()
