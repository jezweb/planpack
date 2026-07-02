#!/usr/bin/env python3
"""Deterministic vector-layer tools for plan sheets.

Subcommands (all take a PDF path + 1-based page number):
  tags <pdf> <page> <label> [...more labels]   Count + locate exact text-tag instances
  words <pdf> <page> [--min-len 2]             Dump all words with coordinates (JSON)
  symbols <pdf> <page>                         Cluster repeated small vector glyphs by
                                               shape signature; report counts per cluster
  measure <pdf> <page> <x0> <y0> <x1> <y1> <scale>
                                               Distance between two points in mm at 1:<scale>

Counting from vector data beats visual counting: the model interprets,
this script counts.
"""
import json
import math
import sys
from collections import defaultdict

import fitz


def page_of(pdf, page_no):
    return fitz.open(pdf)[int(page_no) - 1]


def cmd_tags(pdf, page_no, *labels):
    page = page_of(pdf, page_no)
    words = page.get_text("words")  # x0,y0,x1,y1,word,block,line,word_no
    out = {}
    for label in labels:
        hits = [
            {"x": round((w[0] + w[2]) / 2, 1), "y": round((w[1] + w[3]) / 2, 1)}
            for w in words
            if w[4].strip().upper() == label.upper()
        ]
        out[label] = {"count": len(hits), "positions": hits}
    print(json.dumps(out, indent=1))


def cmd_words(pdf, page_no, *args):
    min_len = 2
    if "--min-len" in args:
        min_len = int(args[args.index("--min-len") + 1])
    page = page_of(pdf, page_no)
    words = [
        {"w": w[4], "x": round((w[0] + w[2]) / 2, 1), "y": round((w[1] + w[3]) / 2, 1)}
        for w in page.get_text("words")
        if len(w[4].strip()) >= min_len
    ]
    print(json.dumps(words))


def hex_colour(c):
    if c is None:
        return None
    return "#" + "".join(f"{round(v * 255):02x}" for v in c)


def shape_signature(d):
    """Coarse signature for one drawing: rounded size + item-type histogram + colours.

    Colours matter: electrical plans distinguish fixture families by fill colour
    alone (identical circles) — without colour every family collapses into one blob
    (observed: a 114-count blob separated into 7 exact families once colour was in the key)."""
    r = d["rect"]
    w, h = round(r.width, 0), round(r.height, 0)
    items = defaultdict(int)
    for it in d["items"]:
        items[it[0]] += 1
    return (w, h, tuple(sorted(items.items())), hex_colour(d.get("fill")), hex_colour(d.get("color")))


def cmd_symbols(pdf, page_no):
    page = page_of(pdf, page_no)
    clusters = defaultdict(list)
    for d in page.get_drawings():
        r = d["rect"]
        # symbols are small repeated glyphs, not walls/borders/hatch fields
        if 2 < r.width < 40 and 2 < r.height < 40:
            clusters[shape_signature(d)].append(
                {"x": round((r.x0 + r.x1) / 2, 1), "y": round((r.y0 + r.y1) / 2, 1)}
            )
    rows = []
    for sig, pos in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
        if len(pos) < 3:
            continue
        # CAD data can hold exact in-place duplicate draw calls (observed: outlets
        # drawn 2-3x at identical positions, single dot visible). Count VISIBLE
        # symbols = unique positions; surface the raw figure so the anomaly is seen.
        uniq = list({(p["x"], p["y"]): p for p in pos}.values())
        row = {
            "signature": {"w": sig[0], "h": sig[1], "items": dict(sig[2]), "fill": sig[3], "stroke": sig[4]},
            "count": len(uniq),
            "sample_positions": uniq[:5],
        }
        if len(uniq) != len(pos):
            row["draw_calls"] = len(pos)
            row["duplicate_positions"] = [
                p for p in uniq if sum(1 for q in pos if (q["x"], q["y"]) == (p["x"], p["y"])) > 1
            ]
        rows.append(row)
    print(json.dumps(rows[:25], indent=1))


def cmd_measure(pdf, page_no, x0, y0, x1, y1, scale):
    pts = math.dist((float(x0), float(y0)), (float(x1), float(y1)))
    mm_on_paper = pts * 25.4 / 72
    real_mm = mm_on_paper * float(scale)
    print(json.dumps({"paper_mm": round(mm_on_paper, 1), "real_mm": round(real_mm), "real_m": round(real_mm / 1000, 3)}))


if __name__ == "__main__":
    cmds = {"tags": cmd_tags, "words": cmd_words, "symbols": cmd_symbols, "measure": cmd_measure}
    if len(sys.argv) < 4 or sys.argv[1] not in cmds:
        print(__doc__)
        sys.exit(1)
    cmds[sys.argv[1]](*sys.argv[2:])
