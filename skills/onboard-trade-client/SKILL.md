---
name: onboard-trade-client
description: Turn a trade business's existing files (past plans, quotes, price data) into a calibrated planpack workspace, ending with a trust report that re-quotes their own past jobs blind. Use when onboarding a trades business to planpack, processing a back-catalogue of past jobs, or asked to "set up my business on planpack".
---

# Onboard a trade client

Goal: a client workspace (`profile.md` + `rates/` + `calibration.md`) built mostly from artefacts the client already has, plus the proof that earns their trust — the system's numbers tested against jobs where *they* know the right answer.

Privacy is absolute: client data stays in their space, their numbers never ship, never appear in public artefacts, never seed another client's defaults. One client is not the trade.

## The flow

1. **Collection matching.** The client hands over a folder-of-everything. Cluster files into jobs (address/project-number/client-name joins — expect alias conflicts) so each job holds its plans, quote(s), POs, correspondence. Money documents (quotes, POs, invoices) are answer keys: **quarantine them immediately**, before any extraction agent runs. What can't be matched to a job is still profile signal (terms templates, insurance certs, rate exports).

2. **Pricing-source import.** Every quoting business has pricing somewhere: an estimating app (ask for an export), a spreadsheet, a supplier-annotated price file, or the estimator's head. Convert what exists to `rates/` markdown tables (UOM | name | material rate | part no | section | labour units — extend per trade). Nothing exists → start from a trade baseline template (openly sourced data + award rates, prices TBD) and let the interview fill it. Audit the card against their real quotes later — expect drift (stale lines, lump entries that never appear in real quotes); surfacing drift is value, not rudeness.

3. **Packs for the back-catalogue.** Build a plan pack per matched job (`build-plan-pack` skill + the trade's lens; independent verifier mandatory — every verifier run on real packs to date has found real errors). Builders never see the quarantined money documents.

4. **Calibration + profile.** Join quote sections to verified takeoffs per the lens's calibration method → `calibration.md` (norms classified stable / variable / underdetermined, each with working and n=). Draft `profile.md`: identity, quote style, standard terms, section vocabulary — plus the interview questions the artefacts can't answer (client-decision toggles, charge-out rates, margin policy). The interview is short because the artefacts did the work.

5. **The trust report (the practice run).** Leave-one-out retrodiction: hold out each job, calibrate on the rest, re-draft the held-out quote blind, score section-by-section against what they actually charged. Present honestly per the lens rules — decomposition, never just totals; fences named; toggles surfaced as the questions we'd have asked. This is the artefact that converts a sceptic: their own job, our blind numbers, side by side.

6. **Go live.** New tender → pack → draft quote in their letter format with their norms applied (cited by n=) and RFIs where only they can decide. They price; we count, derive, and surface. Every live job they accept becomes calibration n+1 — the system gets more theirs with use.

## Failure modes

- Skipping quarantine because "it's just onboarding" — one leaked answer key invalidates the trust report's blindness, which is the whole point.
- Presenting the trust report as accuracy theatre — if a section missed, show it missed and why; the client's confidence survives honest misses, not discovered spin.
- Promoting this client's norms anywhere beyond their workspace.
