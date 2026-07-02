# planpack

Turn construction plan sets into **plan packs**: portable folders any AI agent can query cheaply, with every value carrying provenance and confidence — because these numbers feed real quotes.

A plan pack is what you get when an AI reads a job's drawings the way an estimator does, once, thoroughly — and writes down everything it found in a form you own:

```
my-job/
  CLAUDE.md        how to query this pack (agents read this first)
  job.md           identity, parties, design criteria, conflicts, missing documents
  register.md      every sheet: number, title, revision, status — including listed-but-missing
  objects.json     every marked object with attributes, sheet citations, confidence
  quantities.json  the takeoff: every quantity with its working shown
  coverage.md      what was extracted, what isn't on this job, what isn't derivable
  wiki/            topic pages: site, concrete, framing, services, compliance...
  sheets/          per-sheet renders + text
```

Ask it "what mesh in the garage slab?", "which windows changed in Rev D?", "what's the pier count and where does it come from?" — and get answers with sheet citations, in ~1-2k tokens instead of re-reading a 100k-token PDF every time.

## Install

```
/plugin marketplace add jezweb/planpack
/plugin install planpack
```

Requires Python with PyMuPDF for the deterministic layer (the skill sets this up: `python3 -m venv .venv && .venv/bin/python -m pip install pymupdf`).

## Use

Put a job's PDFs in a folder and ask Claude to **"build a plan pack from ./plans"**. The pipeline: raw render+text layer → document split → sheet register → object extraction (script-counted, not eyeballed) → takeoff quantities with shown workings → **independent verification pass** (every pack, no exceptions) → wiki → done.

For electrical contractors there's a trade lens (`lenses/electrical.md`) covering the four real job shapes (annotated instances, anonymous colour-coded symbols, tag text, prose D&C scope) and the committed-but-undrawn sweep — because on real jobs, what *isn't* drawn is half the quote.

There's also an onboarding skill (`onboard-trade-client`) that turns a business's past jobs + quotes into a calibrated workspace, ending with a trust report: their own past job re-quoted blind, next to what they actually charged.

## Principles

- **Assist, not autopilot.** Packs cite everything, show derivations, and flag what the drawings don't support. The person quoting owns the price.
- **Deterministic where possible.** Counting comes from the PDF's vector layer via script, not from a model's impression of an image.
- **Conflicts are output.** Two sheets disagree → both readings recorded with provenance, flagged as an RFI. Never silently resolved.
- **Verified before shipped.** An independent pass re-derives counts and hunts for misses on every pack.
- **Your data is yours.** Packs are folders you keep. Nothing phones home.

## Web app

Don't use Claude Code/Cowork? The same pipeline runs at [planpack.au](https://planpack.au) — upload plans, browse the pack, download the folder.

---

MIT licence. Built by [Jezweb](https://www.jezweb.com.au), Newcastle, Australia.
