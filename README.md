# Jespersen, *A Modern English Grammar*, Part I: a new edition

A new edition of Otto Jespersen, *A Modern English Grammar on Historical Principles, Part I: Sounds and Spellings* (Heidelberg: Carl Winter, 1909), for Language Science Press, edited by Brett Reynolds and Peter Evans. The model is their edition of Jespersen's *Negation in English and Other Languages* (LangSci book 501, source at <https://github.com/langsci/501>).

This repository holds the transcription pipeline, the editorial decisions and, later, the LaTeX edition. Scans, page images and OCR output stay out of git (`data/`).

## Workflow

1. **Decisions** (editors): base text, misprint policy, notation, how far to regularise. See `DECISIONS.md`.
2. **Python first pass** (`pipeline/firstpass.py`, no language models): render pages, Tesseract OCR with word boxes and confidences, structure (running heads, section numbers, cross-references), and sorting of lines into clean prose and lines needing a closer reading.
3. **Model readings of hard lines only**: line crops sent to two readers from different model families, told to read exactly and flag misprints.
4. **Disagreements**: crops judged by two blind referees; a person sees only what they split on.
5. **People**: the editors clear the queue and proof a random sample of pages in full.
6. **Build**: the langsci template, section labels, linked cross-references and index, apparatus.
7. **Proof**: completeness checks, then the editors' read and LangSci proofreading.

The 2026-11-01 pilot that shaped this workflow is in `Project-Management/experiments/jespersen-meg1-transcription-pilot-2026-11-01/` (portfolio root).

## Layout

```
pipeline/     Python pipeline (step 2 so far)
reports/      generated summaries (statistics only, no page text)
notes/        project brief, source verification queue
data/<scan>/  git-ignored: scan.pdf, pages/, ocr/, lines.jsonl, sections.json, xrefs.json
```

## Running step 2

```bash
make firstpass            # SCAN=1961 by default; needs pdftoppm, pdfinfo, tesseract
```

The scan goes in `data/<scan>/scan.pdf` first. Scans in use are listed in `notes/source-verification.md`.

## Licence

Code: MIT (`LICENSE`). Jespersen's 1909 text is in the public domain. The licence of the edition text will follow Language Science Press (book 501 is CC BY 4.0).
