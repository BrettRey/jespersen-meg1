# Status
<!-- SUMMARY: LangSci edition of Jespersen MEG Part I; scaffolded, step 2 Tesseract first pass run on the 1961 scan · status: active · updated: 2026-11-01 -->

## Current state (2026-11-01)

- Project scaffolded. Working scan: 1961 reprint (`data/1961/scan.pdf`, git-ignored).
- Step 2 first pass run on the whole volume: 508 pages rendered at 300 dpi (74 s) and OCR'd with Tesseract 5.5 (70 s); results in `reports/firstpass-1961.md`.
  - Body runs from PDF page 17; the index from PDF page 472.
  - 16,541 body lines: 43% clean, 39% with notation (brackets or slashes), 18% with a low-confidence word.
  - 851 section heads found, 1.1 to 16.5. 105 places where the order goes backwards; the ones inspected are all Tesseract reading a bold 3 as 8 (1.82 for 1.32, 8.113 for 3.113).
  - 1,357 cross-reference candidates; 297 match no section head found (misread digits, missed heads, references to other volumes).
- Character error rate against the pilot's zoomed Opus reading (9 dense pages): clean lines 0.51% (47 lines), low-confidence 1.68% (12), notation 7.69% (270). The clean-line errors are digits, full stops read as commas, and the notation symbol α on lines without brackets. So clean lines need a second cheap reading too, not automatic acceptance.

## Next actions

1. Repair section numbers: where a head breaks the order and swapping 8 for 3 restores it, accept the swap if the running head's range agrees; list the rest.
2. Add a second independent reading of every line (a second OCR engine or one cheap model pass per page) so clean lines are accepted only where two readings agree.
3. Catch notation symbols outside brackets (α and similar) when sorting lines.
4. When the 1909 scan arrives: check its title page, run step 2 on it, and align it page by page with the 1961 scan to list the 1948 changes.

## Blockers

- Editors' decisions in `DECISIONS.md` (base text, misprint policy, notation).
- 1909 scan: HathiTrust copy is US-only; a US colleague is fetching it.
