#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def extract_vocab_from_lines(lines):
    """Best-effort parser for repeated Word/Meaning two-column exports."""
    idxs = [i for i, line in enumerate(lines) if line.strip().lower() == "word"]
    if len(idxs) < 2:
        return []

    first, second = idxs[0], idxs[1]
    nums, words = [], []
    i = first + 2
    while i < second:
        if re.fullmatch(r"\d+", lines[i].strip()) and i + 1 < second:
            nums.append(int(lines[i].strip()))
            words.append(lines[i + 1].strip())
            i += 2
        else:
            i += 1

    meanings = []
    cur, buf = None, []
    for raw in lines[second + 2 :]:
        line = raw.strip()
        if not line:
            continue
        if line.startswith(("系统词书", "扫描", "下载")) or re.match(r"^共\s*\d+", line):
            break
        if re.fullmatch(r"\d+", line):
            if cur is not None:
                meanings.append((cur, " ".join(buf).strip()))
            cur, buf = int(line), []
        else:
            buf.append(line)
    if cur is not None:
        meanings.append((cur, " ".join(buf).strip()))

    meaning_by_num = dict(meanings)
    return [
        {"index": n, "word": w, "definition": meaning_by_num.get(n, "")}
        for n, w in zip(nums, words)
    ]


def main():
    parser = argparse.ArgumentParser(description="Extract text/pages and simple vocab tables from a PDF.")
    parser.add_argument("pdf")
    parser.add_argument("--out", required=True)
    parser.add_argument("--mode", choices=["auto", "text", "vocab"], default="auto")
    args = parser.parse_args()

    try:
        import fitz
    except ImportError as exc:
        raise SystemExit("PyMuPDF/fitz is required: python3 -m pip install pymupdf") from exc

    pdf = Path(args.pdf)
    doc = fitz.open(str(pdf))
    pages, vocab = [], []
    for page_index, page in enumerate(doc, start=1):
        text = page.get_text("text")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        page_vocab = extract_vocab_from_lines(lines) if args.mode in ("auto", "vocab") else []
        for item in page_vocab:
            item["source_page"] = page_index
        vocab.extend(page_vocab)
        pages.append(
            {
                "page": page_index,
                "text": text,
                "line_count": len(lines),
                "image_count": len(page.get_images(full=True)),
            }
        )

    result = {
        "source": str(pdf),
        "page_count": len(pages),
        "pages": pages,
        "vocab": vocab,
        "vocab_count": len(vocab),
    }
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"pages={len(pages)} vocab={len(vocab)} out={args.out}")


if __name__ == "__main__":
    main()
