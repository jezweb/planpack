# The plan-pack contract (v0.2)

The shared contract everything reads and writes: skills, web tools, MCP servers are all just readers/writers of this folder shape. Discovered from real Australian construction corpora (residential + commercial, hundreds of PDFs) — change it only with corpus evidence.

## Entity model (what real corpora force)

**Job → Files → Documents → Sheets → Objects.** The two non-obvious layers:

- **File ≠ Document.** One 130pp "approval" PDF is often a dozen stapled logical documents (certificate, conditions, energy assessment, geotech, drawings...). One job = PDFs from 4-6 independent consultants. The split step is the pipeline's first real stage. Dedupe at document level (re-exported duplicates with different checksums; `(1)` download collisions).
- **Sheet is the spine, keyed by title-block sheet ID, never page index.** Page order ≠ sheet order; numbering schemes are per-discipline (A2.01 / S05 / C400 / M-4001); title-block position varies by issuer. No unified register exists in the wild — **the pack synthesises one**, and "listed but not present" is first-class (registers advertise A01-A24, the PDF contains A01-A15).

### Job
Canonical identity the pack owns: address + lot/DP + builder job no + client name(s). Every consultant uses their own project number and address strings conflict (suburb spelled two ways, postcode typos) — map aliases to the canonical id, **flag conflicts, never silently pick one**.

### Document
`{type, discipline, issuer/party, local_ref, revision, rev_date, status, file, page_range, text_quality}`
- `status`/maturity matters commercially: architecture "FOR CONSTRUCTION" arrives with structural "PRELIMINARY — NOT FOR CONSTRUCTION" in the same tender. Objects inherit maturity. Below `preliminary` sits `design-development` (client-sketch issues). One sheet can carry two stamps (FOR TENDER + FOR CDC APPROVAL) — record both.
- **Addenda are ordered mutations, not conflicts.** Tender addenda delete, rename and re-quantify marks. Apply in sequence; keep aliases/tombstones so superseded marks still resolve. An addendum outranks the drawing it amends.
- Revision is per-document AND per-sheet (arch Rev E + structural Rev 3 in one job; transmittals give per-sheet issue history). Model supersession; flag cross-document drift ("engineering designed to arch Rev C, folder contains Rev F").
- Dangling references distinguish **absent-but-exists** (the geotech report every structural sheet cites) from **never-existed** (notes citing "electrical engineer's drawings" on a job with no electrical engineer). `listed-only` applies to **spec sections** too, not just sheets (a spec contents table can advertise sections never issued; the tell is blank revision cells).
- Money documents (quotes, purchase orders) are a distinct document class — the client's private pricing data, never extraction input.

### Sheet
`{discipline, sheet_no, group, title, scale, revision, purpose_code, status: present|listed-only, source(file, page), render, text_quality}`

### Object
The dominant pattern everywhere: **mark on plan → schedule row elsewhere** (SF1, EB2, W01, B1.3, SP1, GEF-1). Electrical often breaks it — anonymous colour-coded instances with no marks and no schedule, so `derived` is the confidence ceiling there. So:
`{type, family, mark, attributes{open field-bag}, qty_unit, sheet_refs[], provenance, confidence, maturity}`
- `objects.json` is a **flat JSON array** of these records — no wrapper object (builder metadata goes in coverage.md/job.md). Family names are **singular** (`opening`, `room`), consistent across packs so cross-pack tooling works.
- **A legend is a type dictionary, not scope.** Template legends over-advertise — entries with zero placed instances are common. Only placed instances become objects; verify each legend entry has ≥1 instance.
- **Dedupe derived counts in plan space.** Overlapping detail sheets re-show the same instances. Count on overall plans; use details for room assignment.
- Multi-res jobs scope objects by `dwelling`/unit.
- Area attributes/quantities always name their **boundary convention** (floor-face vs slab-edge vs site) — they differ by several percent and suppliers order to the slab edge.
- **Attributes are an open bag** — the extractor will meet fields no schema anticipated. Promote only the hot fields (below) to indexed/required.
- **Provenance is (party, document, sheet, revision, table-or-quote)** — not just sheet+quote. Two engineers can both assert "N1"; reconcile, don't duplicate.
- **Confidence tiers:** `stated` (schedule row / printed value) > `derived` (counted from tags, joined across sheets) > `scaled` (measured off plan) > `ocr/hand-filled` (scanned forms, stamps). Cross-reference sanity checks upgrade/downgrade `scaled` values.
- **Conflicts are first-class output** (soil class H1 on S1 vs M on S2). A `conflicts` list on the job, each with both provenances.

### Site/design criteria (hot fields, one per job — every structural set carries them)
wind class, soil class, site class, BAL, exposure, concrete grades by element, design loads, geotech ref. These drive quotes and appear in every structural set's criteria block.

### Spec (commercial jobs)
A NATSPEC-style spec is not a sheet — it's a **worksection→clause addressable corpus** (e.g. 0731 Fans), cross-linked to the objects it governs (fan schedule mark ↔ §0731). Drawings give what/where/how-many; specs give to-what-standard/what's-included. A second species exists: the **schedule-of-selections** (spreadsheet-derived, rows map directly to objects, defers to a full spec that may not be in the tender). Revision grain there is per-section and per-row.

### Trade lens (what a trade contractor prices from)
A trade's scope is a **cross-discipline view**, not a discipline folder — electrical jobs routinely have no electrical drawings at all; scope lives on interiors/architectural sheets, prose notes, spec rows, energy-compliance commitments. Per-trade coverage is first-class in the pack (`coverage.md` per trade: derivable / committed-but-undrawn / by-others / tbc). **Scope-boundary flags (`by-others`, `allowance`, `tbc`, `dc-obligation`) are extraction output**, not omissions — they become the quote's exclusions and clarifications. Trade-lens method files live in the skill (`lenses/<trade>.md`); the takeoff groups by the client's own rate-card sections (BYO rate card: UOM | name | material rate | part no | section | labour units).

## Folder shape

```
<job-slug>/
  CLAUDE.md        how to query this pack cheaply; assist-not-autopilot rules; advisory framing
  job.md           canonical identity, parties, design criteria, conflicts, missing-docs
  register.md      synthesised sheet register: doc → sheets, rev, status
  objects.json     the object DB (schema above)
  quantities.json  the takeoff layer: every value with derivation, unit, confidence
  coverage.md      per-family and per-trade attestation: extracted / not present / not derivable
  wiki/            topic pages from notes/specs/schedules — boilerplate deduped
  sheets/<doc>/pNNN.png + pNNN.txt    raw layer (render + text layer)
  source/          original files (or pointers when the pack is shipped without them)
```

Query path an agent follows (written into the pack's CLAUDE.md): register.md + job.md first (~1-2k tokens) → objects.json / quantities.json / wiki page for the topic → only then a specific sheet render. Never open source PDFs first.

## Extraction vocabulary, frequency-rated (from a mixed residential/commercial AU corpus)

| Family | Objects/fields | Frequency |
|---|---|---|
| Slab system | waffle pods (height, spacing, full/cut, start point), slab thickness, mesh grade (SL72-92 T&B), DPM, rib/beam dims, step-downs, articulation joints | every structural set |
| Footings/beams | EB/IB/GEB/DEB/SF/BW/ST marks → section details (dims + reo), trench mesh, trimmers, laps | every structural set |
| Piers | screw (SWL kN, min depth), bored (⌀, socket, MPa), mass concrete; tree/sewer-adjacency drivers | most |
| Reinforcement | bar codes N/R/L/SL/TM + legend, per-element schedules, bar-bending schedules, tonnage | every structural set |
| Steel members | UB/UC/PFC/SHS/RHS/EA sizes, member schedules, connection grammar (n-Mxx bolts, CFW welds), finish (HDG), detail-only members schedules miss | common |
| Timber framing | LVL/MGP marks, framing schedules, bracing (kN req vs achieved), tie-downs | common |
| Openings | W/D/SD marks → schedules (w×h, operation, frame, glazing U/SHGC, sill, hardware) | most |
| Rooms/areas | name, finish, ceiling height, area; area-calc tables; site coverage | every set |
| Electrical | three data shapes: annotated instances (height/no./amp text at each outlet), anonymous colour-coded symbols (legend maps colour→family), text tags (SA/EX/ACU); plus BASIX/NCC committed-but-undrawn scope (LED lighting, smoke alarms, ceiling fans "refer NatHERS"), equipment schedules as load ledgers (amps/phase/hardwired), supply origin from the survey layer | varies — see lens |
| Mechanical | fan/hood/grille schedules (duty, power, sound), duct sizing | commercial |
| Civil/stormwater | pipe runs (⌀, material, grade, invert levels), pits, tanks, cut/fill | some |
| Site | boundaries (bearing/distance), easements, FFL/RL/NGL, services connections, retaining | most |
| Compliance | BASIX commitments + glazing schedule, BCA/NCC clause tables, AS refs (cite clause numbers as printed — never ingest licensed standard text), approval conditions, inspection hold points | most |

## Pipeline implications (bind the build)

1. **Two ingestion paths from day one:** text-layer (cheap, ~90% of born-digital corpora) and vision-on-render (raster sheets, outlined-vector text, scanned forms, approval stamps — image overlays invisible to text extraction).
2. **Tables need geometry or vision** — naive text extraction shreds schedule rows. Schedules are where the value lives.
3. **Sheet identification is a model job** (title blocks vary too much for regex).
4. **Boilerplate dedupe** — repeated general-notes blocks pollute extraction.
5. **The estimator's vocabulary is the target vocabulary**: extracted objects should map to the materials and line items real quotes use, so quantities feed a calculator — and the client's own past quotes/POs let the pack be validated against reality.
