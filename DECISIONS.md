# Decisions
<!-- SUMMARY: decision log for the LangSci edition of Jespersen MEG Part I · status: active · updated: 2026-11-01 -->

2026-11-01 — Project created at `books/jespersen-meg1/` as a new LangSci edition of MEG Part I, edited by Brett Reynolds and Peter Evans, on the model of the *Negation* edition (langsci/501). Brett's decision after the transcription pilot.

2026-11-01 — Workflow: Python and Tesseract read every page first; models read only crops of hard lines; blind referees from two model families settle disagreements; the editors see only what the referees split on. Reason: the pilot (`Project-Management/experiments/jespersen-meg1-transcription-pilot-2026-11-01/README.md`) found model disagreements concentrated in phonetic notation, while Tesseract reads prose almost cleanly in under a second a page and keeps misprints as printed.

2026-11-01 — Scans, page images and OCR output stay out of git (`data/` ignored); reports carry statistics only. Reason: the working scan is a third-party upload of a reprint that contains Haislund's 1948 material, and scans are large.

2026-11-01 — Working scan: 1961 Allen & Unwin reprint (photographic reprint of the 1909 setting with Haislund's 1948 changes). Base text intended to be the 1909 printing, once a scan is confirmed (candidate: HathiTrust `njp.32101075727741`). Final choice is for the editors.

2026-11-01 — Code licensed MIT. Edition text licence to be set with LangSci. Setup default, reversible.

2026-11-01 — LaTeX scaffold deferred. The edition will be built from the langsci template used for book 501, not the portfolio paper template, once transcription exists. So there is no `main.tex` yet.

## Open decisions for the editors

- Base text: 1909 printing, with the 1948 changes adopted or recorded in an apparatus.
- Misprint policy: keep as printed, or correct and list each correction.
- Notation: keep Jespersen's symbols with a table mapping them to IPA, or convert.
- How far to regularise, as the *Negation* edition did (abbreviations, linked sources).
- Use of the Routledge reissues (UofT licence terms; Haislund's rights in Parts VI and VII).

## Connections to sibling work

- langsci/501 *Negation* edition: **adopted** (template, conventions, LangSci Classics series).
- `books/language-landscapes/` (LangSci book 555): **adopted** for LangSci production experience only.
- Transcription pilot, 2026-11-01: **adopted** as the evidence base for the workflow.
