# Project brief
<!-- SUMMARY: goals, constraints and evidence for the Jespersen MEG Part I edition · status: active · updated: 2026-11-01 -->

## Goal

A new edition of Jespersen, *A Modern English Grammar on Historical Principles, Part I: Sounds and Spellings* (1909) for Language Science Press, edited by Brett Reynolds and Peter Evans, on the model of their *Negation* edition (LangSci 501). The *Negation* edition took most of a year with older models (o3 era). The question was how much faster current tools make Part I, and whether the other six parts could follow.

## Evidence so far (2026-11-01 pilot)

Full results: `Project-Management/experiments/jespersen-meg1-transcription-pilot-2026-11-01/README.md`.

- On the nine densest notation pages, two independent model readings disagreed about 4.5 times a page; two blind referees from different model families settled about 85% of those, leaving under one decision a page for a person.
- Disagreements cluster in the phonetic notation (27 of 41). Outside it, models agree on almost every character.
- Single-look readers (Opus, Sonnet, Muse) quietly correct Jespersen's misprints, and do so identically, so no disagreement exposes the correction. A reader that zooms (about 104k tokens a page) catches them.
- Tesseract reads a page in under a second; prose comes through nearly clean, notation does not (124 of 134 disagreements with the zoomed Opus reading on p359 were inside transcriptions). It is literal: the scan's old OCR kept *withcut*, *chancelor\**, *Orrm's* as printed.
- Local Qwen (about 10 min a page) and Apple's on-device model (blocked by its safety filter) are not practical.

## Constraints

- Part I is notation-dense: roughly 5,000 lines of bracketed or slashed transcription.
- The 1961 reprint includes Haislund's 1948 changes; a 1909 scan is needed to separate them.
- Licensed copies (Routledge via UofT) must not go to external models before the licence is checked.
- Haislund assisted with Part VI and completed Part VII; his rights status is unverified.

## Rough scale

Part I: about 508 scanned pages. All seven parts: about 3,800 scanned pages (Part I 508, II 552, III ~436, IV ~440, V ~554, VI 585, VII 712; III to V from archive.org image counts).
