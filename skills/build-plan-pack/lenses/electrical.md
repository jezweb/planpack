# Electrical trade lens

Load this when building a pack for an electrical contractor, or adding the electrical trade view to any pack. Discovered from real electrical tender corpora (commercial fit-out, tenancy refurb, residential new build) and validated against the contractors' actual submitted quotes.

## The core fact

Electrical is a **lens over the whole set, not a discipline folder**. On real jobs there is frequently no electrical engineer at all: scope lives on interiors sheets, architectural floor plans, prose notes, spec rows. Sweep every sheet and document for electrical-relevant content; never filter to "electrical drawings" (there usually aren't any).

## Job shapes (detect at classification, they change the method)

1. **Annotated instances** (common on fit-out/interiors sets): each placed outlet carries text annotations (HEIGHT / NO. / AMP / phase). Take off via `words` + proximity join — the annotations ARE the schedule. Symbol clustering fails on fragmented arc glyphs.
2. **Anonymous symbols** (common on residential lighting plans): identical glyphs distinguished only by fill colour, no marks, no schedule. Take off via `symbols` (colour is in the signature) — map each colour cluster to its legend entry, verify one cluster with a high-DPI crop, then trust counts. Confidence ceiling is `derived` (nothing is "stated" anywhere).
3. **Tag text on plans** (common on architectural sets): SA / EX / ACU as text tags. Take off via `tags`, counted on the **overall** plan; detail sheets that overlap ("Plan / Plan Continued") re-show the same instances — dedupe in plan space or count only on overalls.
4. **Prose scope / D&C** (fit-out tenders): no placed instances at all — a note transfers design responsibility ("electrical contractor responsible for design, install and certifying"). The extraction unit is the **scope clause** — contractor notes, spec rows, addenda. The pack's job is the scope ledger: every fixed load with its source row, every design-and-construct obligation, every phantom reference.

Real jobs mix shapes; classify per sheet, not per job.

## Where committed-but-undrawn scope hides (sweep all of these)

- **BASIX / Section J / NatHERS commitments**: LED lighting per room class, AC systems, exhaust interlocks, ceiling fans ("refer to NatHERS certificate" — chargeable items whose count lives in an absent document). These are commitments the contractor must price, with provenance.
- **NCC-mandated systems never drawn**: smoke alarms (AS 3786 interconnected), exit/emergency lighting in commercial. If the job type mandates it and nothing is drawn, it's an allowance line, not a gap.
- **Appliance/equipment schedules**: the load ledger (amps, phase, hardwired vs GPO). Kitchen equipment, lifts, HWS, pumps, AC condensers — each is a circuit + connection. Loads hide in other trades' rows too (a sensor tap or urinal is a 240V connection sitting in a plumbing schedule).
- **Contractor notes on architectural sheets**: D&C transfers, mounting heights, board condition investigations.
- **Survey layer**: supply origin (power pole, service pit, meter position) — provenance is the surveyor, not the hosting sheet's issuer.
- **Addenda**: ordered mutations of the object set (marks deleted, renamed, quantities changed). Apply in sequence with aliases/tombstones; an addendum row outranks the drawing it amends.
- **Tenancy-services defaults** (retail/commercial fit-outs): NBN lead-in/pathways, MATV/AV distribution, and per-point comms reticulation are priced on virtually every tenancy job yet almost never drawn. If the job is a fit-out and they're absent from the documents, they're allowance lines by default — name them explicitly.

## Traps

- **Template legends over-advertise.** Legend boxes list symbols with zero placed instances. A legend is a type dictionary — only placed instances become objects. Verify every legend entry has ≥1 instance before extracting it as scope.
- **Colour-blind clustering merges families.** Identical circles differing only by fill collapse into one blob; `vector_tools.py symbols` keys on fill+stroke colour for exactly this reason.
- **Overlap double-counting** (shape 3 above).
- **The absence list is half the quote.** On real benchmarked jobs, counted points covered roughly half of quote value. Switchboards, mains, circuit runs, data, security are routinely undrawn — a takeoff that reports only what it counted reads as complete and underprices the job.

## Output: takeoff keyed to the client's rate-card sections

Group `quantities.json` entries by the sections the client's own rate card uses. Three entry kinds, all first-class:

- **counted**: deterministic count/length with derivation + sheet refs (confidence `derived`).
- **allowance**: committed or mandated scope with no drawn quantity — state the driver ("energy assessment: LED lighting to every habitable room; 14 rooms listed on the floor plans") so the estimator prices from the driver, not a guess. Never invent a count.
- **excluded / by-others / tbc**: explicit scope boundaries found in the documents ("lighting layout not available at time of tender", "security to client specification", fire by others). These become the quote's exclusions and clarifications sections — as valuable as the counts.

Draft-quote assembly (when a rate card is present): counted × matching rate-card line (match on UOM + name/section), allowances listed with drivers for manual pricing, exclusions/clarifications from the scope flags + the client's standard terms. Every line cites its source. The client prices; we count and surface.

**Calibration from the client's own history** (when past quote/job pairs exist): join each quote's section totals to a verified pack takeoff of the same job, then classify every derived norm **stable** (consistent across n≥2 jobs — usable as a default in that client's drafts), **variable** (state the job-shape dependency), or **underdetermined** (n=1 or a lump that won't decompose — never default). Norms carry their working and n=. Expect the client's own artefacts to drift (totals that don't recompute, stale rate lines) — surfacing that drift is product value, not rudeness. Output: `calibration.md` + `profile.md` (identity, quote style, standard terms, and the interview questions the artefacts can't answer) in the client's private space.

What transfers (proven by a leave-one-out test on a real client's history): token/unit values, presence rules, format/vocabulary, methods and ratios — and the hold-back discipline (declining to apply a wrong-shape norm avoids phantom lines). What does NOT transfer: **client-decision toggles** (e.g. whether a data system is in scope — that lives in an inclusions list, not the drawings; surface it as a question to the client, never assume a mode) and section taxonomy at scales the history hasn't seen.

**One client is not the trade.** Everything derived from a client's own artefacts — section vocabulary, quote style (lump-sum letter vs itemised), allowance norms, unit-rate calibration — is that client's profile, not an electrical-trade default. What generalises is the method; the numbers and preferences stay per-client config. Never promote one client's norms into shipped defaults.

Two rules real benchmarks forced:

- **Lump rate-card lines need a scale-or-confirm gate.** Some lines carry whole-project labour (e.g. a 50-hour "disconnect all services" line). Multiplying or carrying one into a per-item takeoff swamps the total — if a line's labour is implausible for a single instance, hold it PRICE-ON-REVIEW rather than letting it into the headline number.
- **Report the decomposition, never the total.** The honest claim is "counted base $X + allowance ledger correctly naming where the rest lives", not "within N% of the real quote" — totals can agree by offsetting errors. If a benchmark total matches but the composition doesn't, say so.
