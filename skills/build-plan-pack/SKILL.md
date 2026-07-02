---
name: build-plan-pack
description: Turn a construction job folder (PDF plan sets, engineering, approvals, specs) into a queryable plan pack — synthesised sheet register, object database with provenance+confidence, takeoff quantities with shown workings, topic wiki, per-sheet renders. Use when asked to "build a plan pack", "index these plans", "do a takeoff", or process a folder of construction drawings for AI querying.
---

# Build a plan pack

Goal: a portable folder any AI agent can query for ~1-2k tokens instead of re-reading megabytes of PDF — with every value carrying provenance and confidence, because these numbers feed real quotes. The output contract is `references/pack-contract.md` (next to this file) — read it first; it was discovered from real construction corpora and encodes traps you will otherwise rediscover (file ≠ document, sheets keyed by title block not page index, conflicting sheets, listed-but-absent drawings).

When the pack serves a specific trade, also read `lenses/<trade>.md`: a trade's scope is a cross-discipline view over the whole set — the lens carries that trade's job shapes, counting techniques, the committed-but-undrawn scope sweep, and how the takeoff should speak the client's rate-card vocabulary.

Setup once per machine: `python3 -m venv .venv && .venv/bin/python -m pip install pymupdf` (the scripts need PyMuPDF).

## Method

1. **Raw layer (deterministic).** `.venv/bin/python "${CLAUDE_PLUGIN_ROOT}/scripts/sheet_extract.py" <job-folder> <pack-dir>` renders every page to PNG + extracts the text layer + per-page stats into `sheets.json`. Zero-text pages are your signal for raster/outlined-vector content that needs the visual path.

2. **Document split & classify (judgment — yours).** Using sheets.json stats + page text + renders where needed, partition each file into logical documents: type, discipline, issuer, revision, status/maturity, page range. Boundary signals ranked: header/footer identity change, page-number restarts, orientation flips, text→raster transitions. Dedupe re-exports and `(1)` collisions at document level. Merged approval bundles (one PDF = a dozen stapled documents) are normal, not an edge case.

3. **Register synthesis.** Identify every sheet from its title block (read the render — title-block position and format vary by issuer; regex will lie to you). Capture any printed drawing list/transmittal, and record listed-but-not-present sheets. Write `register.md`. The register is also the extraction routing table — a sheet wrongly marked irrelevant to a trade silently exits every downstream pass, so when in doubt mark it relevant.

4. **Object extraction.** Fan out subagents per document (or per discipline for big sets). The dominant pattern is mark-on-plan → schedule-row-elsewhere; schedules are where the value lives, and text extraction shreds table rows — read schedules from the render when in doubt. Extract into `objects.json` per the contract: open attribute bag, provenance (party, document, sheet, revision, table/quote), confidence tier (stated > derived > scaled > ocr). Sanity-check scaled values against known dimensions. Record contradictions between sheets in job.md — never resolve them silently.

   **Count with the script, not your eyes.** `"${CLAUDE_PLUGIN_ROOT}/scripts/vector_tools.py"` counts deterministically from the vector layer: `tags <pdf> <page> EB1 EB2 ...` (exact tag instances with positions), `symbols <pdf> <page>` (repeated glyph clusters keyed by shape AND fill/stroke colour — verify what a cluster IS with one high-DPI crop, then trust its count), `words` (all text with coordinates, for spatial joins), `measure` (point-to-point at a stated scale — always sanity-check against a known dimension). A script count of the plan's own vector data outranks any visual estimate, including one in ground truth. Visual counting is a last resort for raster sheets only, and must be flagged approximate.

   **Trap: born-digital PDFs can embed raster sub-layers.** A vector sheet may carry part of its content as an embedded image — the script then counts only the vector-drawn portion and the count is silently low. Cross-check every symbol count against a high-DPI render read; when the layers disagree, state both bases (vector n + raster ~m) rather than one number.

   **Trap: CAD files hold exact in-place duplicate draw calls** — one visible symbol, 2-3 identical draw records. `symbols` counts unique positions and reports `draw_calls` when they differ; if you count vector records any other way, dedupe positions first. The mirror error also exists: don't "correct" a script count against a claim that itself was never re-derived.

   **Trap: overlapping detail sheets re-show the same instances** ("Plan / Plan Continued"). Count on overall plans; use details for room/zone assignment; dedupe derived counts in plan space.

   **Sweep exhaustively, then attest.** After schedule/table extraction, sweep each plan sheet's annotations (every tag, label, callout — `words` output makes this cheap) and reconcile against your objects. Then write a coverage attestation into the pack (`coverage.md`): for every family in the contract vocabulary, either "extracted (n objects)" or "not present on this job" — a silent gap reads as "covered" to the next agent, which is how answerable questions get declined.

5. **Quantities (the takeoff layer).** A pack that only describes the building declines the questions estimators actually ask. Derive `quantities.json`: the take-off a competent estimator would produce from these drawings — areas by zone, runs, enumerated counts, material quantities where derivable. Every quantity shows its working: `{quantity, value, unit, derivation: "inputs (cited) → method → result", sanity_check, confidence: "derived"}`. Never present a derived quantity as stated; the working is what makes it checkable and therefore usable in a quote.

   **State the boundary convention on every area.** "Floor area" (to wall face, what architects' area tables state) and "slab area" (to slab edge, what suppliers order and quote) differ by several percent. An area without its convention named is not usable in a quote. Give both when both are derivable.

6. **Verify (independent) — every pack, no exceptions.** A separate agent (not the extractor — the producer shares the blind spot that made the miss) walks each sheet against objects.json + quantities.json + coverage.md AND the register: spot-checks stated values against renders, re-runs the script counts, hunts for annotations present on sheets but absent from the pack, and verifies register claims — register errors propagate straight into query answers. Every verifier run on real packs to date has found real errors, including in packs that looked clean. Its findings get fixed before the pack ships.

7. **Wiki.** Topic pages (site, concrete, reinforcement, openings, framing, services, compliance — only the topics this job actually has) from general notes, specs, and schedules. Dedupe boilerplate: engineer standard-notes sheets repeat across jobs; summarise once, cite the sheet. For spec documents, one page per worksection, linked to the objects it governs.

8. **job.md + pack CLAUDE.md.** Canonical job identity (address, lot/DP, job numbers per party — flag alias conflicts), parties, design criteria (wind/soil/site class, BAL, concrete grades — every structural set has these), conflicts, referenced-but-absent documents. The pack CLAUDE.md tells a querying agent: register + job first, then objects/wiki, sheet renders only for verification — and that every answer must cite (sheet, revision) and carry advisory framing.

9. **Verify by inspection.** Pick 5 values from objects.json, open the cited sheet renders, confirm each. If any is wrong, the extraction pass has a systematic problem — find it before shipping the pack.

Write each artefact to disk as soon as its content is determined (register after identification, objects after extraction, wiki pages as composed) — pack builds are long-running and a mid-run death must leave a resumable disk state, not a lost analysis.

## Failure modes to watch

- Trusting the text layer for schedules and title blocks (geometry shreds rows; stamps and hand-filled forms are invisible to text extraction).
- Treating the folder as one document or the PDF as one revision — maturity and revision drift are per-document facts an estimator prices by.
- Quantities without provenance. An uncited number in a pack is worse than no number: it will be quoted.
- Money documents (quotes, purchase orders, invoices) leaking into extraction input. They're the client's private data and, when benchmarking, they're answer keys — never extraction input.

## Advisory framing (non-negotiable)

Packs assist estimators; they don't replace them. Every value cites its source; derived values show their working; scope the drawings don't support is flagged, not guessed. The person quoting owns the price.
