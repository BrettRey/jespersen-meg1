# CLAUDE.md: Jespersen MEG Part I edition

Your role here is editor and pipeline engineer for a new edition of Jespersen, *A Modern English Grammar on Historical Principles, Part I: Sounds and Spellings* (1909), for Language Science Press. Editors: Brett Reynolds and Peter Evans. Don't make editorial commitments on Peter's behalf.

Read `STATUS.md` and `DECISIONS.md` first. `README.md` has the seven-step workflow; portfolio rules in `../../.claude/rules/` apply.

## Hard rules

- **Scans, page images and OCR output never go in git.** They live in `data/` (ignored). Reports in `reports/` carry statistics only.
- **Licensed copies stay local.** The Routledge reissues available through the University of Toronto library are licensed e-books. Don't send their pages to any external model (Astra, Muse, OpenRouter, or the Claude API) until the licence terms have been checked and recorded in `DECISIONS.md`. Tesseract runs locally and is fine.
- **Step 2 uses no language models.** `pipeline/firstpass.py` is deterministic Python and Tesseract.
- **Transcription is exact until the misprint policy is settled.** Models must flag a suspected misprint, never silently fix it. The pilot found that cheap readers correct Jespersen's misprints (e.g. *twopencc*), and two readers make the same correction, so no disagreement exposes it.
- **Hyphen vs length mark.** In this typeface a hyphen inside brackets is wider than tall and sits at mid-height; Jespersen's length mark is a roughly square dot at the top of the letters. Put this in every transcription prompt.

## Scans

- `data/1961/scan.pdf`: 1961 Allen & Unwin reprint, a photographic reprint of the 1909 setting with Niels Haislund's 1948 changes (his note follows Jespersen's preface). Working scan until the 1909 printing arrives.
- 1909 printing: best candidate is HathiTrust `njp.32101075727741` (Princeton), full view in the US only. A US colleague is fetching it. Check its title page (Carl Winter, Heidelberg, 1909; no edition statement) before using it.

## Model routing

Follow `.claude/rules/multi-model-dispatch.md`. For bulk readings, use direct API or CLI calls (Codex, `muse exec --model muse-wonder-1.0` from an isolated folder), not Claude Code subagents, whose token overhead is several times the job. Every model reading is a candidate until the referee step or an editor settles it.
