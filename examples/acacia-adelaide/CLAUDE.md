# Acacia House (Adelaide) — plan pack

This folder is a **plan pack**: one thorough read of a drawing set, written down so any AI agent can answer questions from it cheaply. This example is built from the Australian Government's *Design For Place* "Acacia House" (Adelaide variant) technical drawings.

> Source drawings: © Commonwealth of Australia 2026. Design For Place is licensed under CC BY 4.0, and provided free of charge at www.yourhome.gov.au. This set is **Preliminary stage** — a complete architectural design, not construction documentation.

## How to query this pack

1. Read `register.md` + `job.md` first (~1-2k tokens) — sheet map, identity, headline figures, conflicts.
2. Then `objects.json` (44 records: openings, rooms, site, cladding, compliance...) and `quantities.json` (18 entries, every value with derivation) or the `wiki/` page for your topic.
3. Open a render in `sheets/` only to verify a specific value — never re-read the source PDF first.
4. `coverage.md` tells you what this set does NOT carry (no structural, no electrical layout, no hydraulic/mechanical design) — decline those questions with a citation instead of guessing.

## Rules for answers

- Every answer cites its sheet (e.g. "2/10 NOTES") and carries the pack's confidence tier.
- Derived values are quoted with their working; never present them as stated.
- Advisory framing always: this pack assists estimation and design review; the person quoting owns the price. The set's own disclaimer (guide only) applies on top.
