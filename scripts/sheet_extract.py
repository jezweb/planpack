#!/usr/bin/env python3
"""Deterministic sheet extraction: PDF(s) → per-sheet PNG + text + metadata.

Usage:
  .venv/bin/python scripts/sheet_extract.py <pdf-or-folder> <output-dir> [--dpi 150]

For each page of each PDF: renders sheets/<doc>/<page>.png, writes
sheets/<doc>/<page>.txt (raw text layer), and appends a row to sheets.json
(doc, page, text chars, image count, vector path count, page size, guessed
sheet number/title from title-block region text).

This is the raw layer under a plan pack. It makes no schema decisions.
"""
import json
import re
import sys
from pathlib import Path

import fitz

DPI = 150
if "--dpi" in sys.argv:
    DPI = int(sys.argv[sys.argv.index("--dpi") + 1])

src = Path(sys.argv[1])
out = Path(sys.argv[2])
pdfs = sorted(src.rglob("*.pdf")) if src.is_dir() else [src]
pdfs = [p for p in pdfs if not p.name.startswith("._")]

SHEET_NO = re.compile(r"\b([A-Z]{1,3}[-.]?\d{1,3}(?:\.\d{1,2})?(?:\s*(?:of|/)\s*\d+)?)\b")

rows = []
for pdf in pdfs:
    slug = re.sub(r"[^a-z0-9]+", "-", pdf.stem.lower()).strip("-")[:60]
    doc_dir = out / "sheets" / slug
    doc_dir.mkdir(parents=True, exist_ok=True)
    try:
        doc = fitz.open(pdf)
    except Exception as e:
        rows.append({"doc": slug, "source": str(pdf), "error": str(e)})
        continue
    for i, page in enumerate(doc, start=1):
        png = doc_dir / f"p{i:03d}.png"
        txt = doc_dir / f"p{i:03d}.txt"
        if not png.exists():
            page.get_pixmap(dpi=DPI).save(png)
        text = page.get_text()
        txt.write_text(text)
        # title block is conventionally bottom-right: sample that quadrant's text
        r = page.rect
        tb = page.get_text(clip=fitz.Rect(r.width * 0.6, r.height * 0.75, r.width, r.height))
        sheet_no = None
        m = SHEET_NO.findall(tb)
        if m:
            sheet_no = m[-1]
        rows.append({
            "doc": slug,
            "source": str(pdf),
            "page": i,
            "png": str(png.relative_to(out)),
            "text_chars": len(text),
            "images": len(page.get_images()),
            "vector_paths": len(page.get_drawings()),
            "size_mm": [round(r.width * 25.4 / 72), round(r.height * 25.4 / 72)],
            "titleblock_guess": " ".join(tb.split())[:200],
            "sheet_no_guess": sheet_no,
        })
    doc.close()

out.mkdir(parents=True, exist_ok=True)
(out / "sheets.json").write_text(json.dumps(rows, indent=1))
ok = [r for r in rows if "error" not in r]
print(f"{len(pdfs)} PDFs → {len(ok)} sheets → {out}/sheets.json")
errs = [r for r in rows if "error" in r]
if errs:
    print("errors:", [r["source"] for r in errs])
