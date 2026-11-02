#!/usr/bin/env python3
"""Step 2: deterministic first pass over a scanned volume of Jespersen's MEG Part I.

    python3 pipeline/firstpass.py render --scan 1961   # PDF -> 300 dpi grey page images
    python3 pipeline/firstpass.py ocr    --scan 1961   # Tesseract word boxes + confidences per page
    python3 pipeline/firstpass.py parse  --scan 1961   # lines, line classes, sections, cross-references
    python3 pipeline/firstpass.py report --scan 1961   # summary + check against the pilot transcriptions

Everything lives under data/<scan>/ (git-ignored). Only the summary report is written to reports/.
No language model is called anywhere in this file.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT.parent.parent / "Project-Management/experiments/jespersen-meg1-transcription-pilot-2026-11-01"

LOWCONF = 70          # a word below this Tesseract confidence makes its line "lowconf"
NOTATION = re.compile(r"[\[\]/|]")   # brackets and slashes; Tesseract often reads "]" as "|"
SECTION_HEAD = re.compile(r"^\s*(\d{1,2})[.,](\d{1,3})[.,]?(?=\s|$)")
XREF = re.compile(r"(?<![\d.,])(\d{1,2})\.(\d{1,3})(?![\d])")


def d(scan: str) -> Path:
    return ROOT / "data" / scan


# ---------------------------------------------------------------- render
def render(scan: str) -> None:
    pdf = d(scan) / "scan.pdf"
    out = d(scan) / "pages"
    out.mkdir(exist_ok=True)
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                                                          text=True).stdout).group(1))

    def one(p: int) -> None:
        dest = out / f"p{p:03d}.png"
        if not dest.exists():
            subprocess.run(["pdftoppm", "-r", "300", "-gray", "-png", "-f", str(p), "-l", str(p),
                            "-singlefile", str(pdf), str(dest.with_suffix(""))], check=True)

    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
        list(ex.map(one, range(1, n + 1)))
    print(f"rendered {n} pages -> {out}")


# ---------------------------------------------------------------- ocr
def tesseract(png: Path, outbase: Path, psm: int) -> None:
    env = dict(os.environ, OMP_THREAD_LIMIT="1")
    subprocess.run(["tesseract", str(png), str(outbase), "-l", "eng", "--psm", str(psm), "tsv"],
                   check=True, capture_output=True, env=env)


def ocr(scan: str) -> None:
    pages = sorted((d(scan) / "pages").glob("p*.png"))
    out = d(scan) / "ocr"
    out.mkdir(exist_ok=True)
    jobs = [(p, out / p.stem) for p in pages if not (out / f"{p.stem}.tsv").exists()]
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
        list(ex.map(lambda j: tesseract(j[0], j[1], 6), jobs))
    # The index is in columns: find where it starts and redo those pages with automatic layout.
    start = index_start(scan)
    if start:
        idx = [p for p in pages if int(p.stem[1:]) >= start]
        marker = out / ".index-psm3-done"
        if not marker.exists():
            with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
                list(ex.map(lambda p: tesseract(p, out / p.stem, 3), idx))
            marker.write_text(str(start))
    print(f"OCR done for {len(pages)} pages; index starts at PDF page {start}")


def read_tsv(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r.get("level") == "5" and (r.get("text") or "").strip():
                rows.append(r)
    return rows


def page_text(scan: str, stem: str) -> str:
    return " ".join(r["text"] for r in read_tsv(d(scan) / "ocr" / f"{stem}.tsv"))


def index_start(scan: str) -> int | None:
    for tsv in sorted((d(scan) / "ocr").glob("p*.tsv")):
        if "chapters and sections" in page_text(scan, tsv.stem).lower():
            return int(tsv.stem[1:])
    return None


# ---------------------------------------------------------------- parse
def lines_of(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        groups[(int(r["block_num"]), int(r["par_num"]), int(r["line_num"]))].append(r)
    lines = []
    for key, words in groups.items():
        words.sort(key=lambda w: int(w["word_num"]))
        x0 = min(int(w["left"]) for w in words); y0 = min(int(w["top"]) for w in words)
        x1 = max(int(w["left"]) + int(w["width"]) for w in words)
        y1 = max(int(w["top"]) + int(w["height"]) for w in words)
        confs = [float(w["conf"]) for w in words]
        lines.append({"key": key, "bbox": [x0, y0, x1, y1],
                      "text": " ".join(w["text"] for w in words),
                      "min_conf": round(min(confs), 1), "mean_conf": round(sum(confs) / len(confs), 1),
                      "low_words": [w["text"] for w in words if float(w["conf"]) < LOWCONF]})
    lines.sort(key=lambda l: l["key"])   # Tesseract's own reading order (columns stay together)
    return lines


def body_start(scan: str) -> int:
    """Page of the last section head 1.1 among the opening pages. The contents list 1.1 too, so the
    first occurrence is front matter; the body's own 1.1 comes after it."""
    hits = []
    for tsv in sorted((d(scan) / "ocr").glob("p*.tsv"))[:40]:
        for ln in lines_of(read_tsv(tsv))[1:]:
            m = SECTION_HEAD.match(ln["text"])
            if m and m.group(1) == "1" and m.group(2) == "1":
                hits.append(int(tsv.stem[1:]))
    return max(hits) if hits else 1


def parse(scan: str) -> None:
    start = index_start(scan) or 10 ** 6
    first = body_start(scan)
    out_lines = d(scan) / "lines.jsonl"
    sections, xrefs = [], []
    with out_lines.open("w", encoding="utf-8") as fo:
        for tsv in sorted((d(scan) / "ocr").glob("p*.tsv")):
            pno = int(tsv.stem[1:])
            region = "index" if pno >= start else "body" if pno >= first else "front"
            lines = lines_of(read_tsv(tsv))
            for i, ln in enumerate(lines):
                reasons = []
                if NOTATION.search(ln["text"]):
                    reasons.append("notation")
                if ln["low_words"]:
                    reasons.append("lowconf")
                cls = "head" if i == 0 else ("notation" if "notation" in reasons else
                                             "lowconf" if "lowconf" in reasons else "clean")
                rec = {"page": pno, "line": i, "region": region, "class": cls, "reasons": reasons, **ln}
                rec.pop("key")
                fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
                if region == "body" and i > 0:
                    m = SECTION_HEAD.match(ln["text"])
                    if m:
                        sections.append({"sec": f"{int(m.group(1))}.{m.group(2)}", "page": pno, "line": i})
                    for x in XREF.finditer(ln["text"]):
                        if m and x.start() <= m.end():
                            continue
                        xrefs.append({"ref": f"{int(x.group(1))}.{x.group(2)}", "page": pno, "line": i})
    (d(scan) / "sections.json").write_text(json.dumps(sections, indent=0))
    (d(scan) / "xrefs.json").write_text(json.dumps(xrefs, indent=0))
    print(f"parsed: {sum(1 for _ in out_lines.open())} lines, {len(sections)} section heads, "
          f"{len(xrefs)} cross-reference candidates")


# ---------------------------------------------------------------- report
def sec_key(s: str) -> tuple:
    ch, frac = s.split(".")
    return (int(ch), frac)          # fraction compared as a digit string = decimal order


def levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"\\(textit|textbf|textsc|spaced)\{", "", s)
    s = re.sub(r"\{\?\}", "", s)
    s = re.sub(r"\{\?([^{}]*)\}", r"\1", s)
    s = s.replace("{", "").replace("}", "").replace("=====COLUMN=====", "")
    return re.sub(r"\s+", " ", s).strip()


def validate(scan: str, records: list[dict]) -> dict:
    """Character error rate of Tesseract lines, by class, against the pilot's zoomed Opus 5.5
    transcriptions (a model reading, not ground truth). Pilot page stems are PDF page numbers of
    the same 1961 scan, so this only runs for that scan."""
    ref_dir = PILOT / "outputs/anthropic_claude-opus-5.5"
    if scan != "1961" or not ref_dir.exists():
        return {}
    import difflib
    by_page = defaultdict(list)
    for r in records:
        by_page[r["page"]].append(r)
    stats = defaultdict(lambda: [0, 0, 0])  # class -> [lines, edits, ref chars]
    for ref in sorted(ref_dir.glob("p*.txt")):
        pno = int(ref.stem[1:])
        if pno not in by_page or by_page[pno][0]["region"] == "index":
            continue
        ref_lines = [norm(l) for l in ref.read_text().splitlines() if norm(l)]
        ocr_lines = by_page[pno]
        sm = difflib.SequenceMatcher(None, [norm(l["text"]) for l in ocr_lines], ref_lines, autojunk=False)
        # pair lines positionally inside matched/replaced blocks of equal length
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op in ("equal", "replace") and (i2 - i1) == (j2 - j1):
                for k in range(i2 - i1):
                    o, rf = ocr_lines[i1 + k], ref_lines[j1 + k]
                    s = stats[o["class"]]
                    s[0] += 1; s[1] += levenshtein(norm(o["text"]), rf); s[2] += len(rf)
    return {c: {"lines": v[0], "cer": round(v[1] / v[2], 4) if v[2] else None} for c, v in stats.items()}


def report(scan: str) -> None:
    records = [json.loads(l) for l in (d(scan) / "lines.jsonl").open(encoding="utf-8")]
    sections = json.loads((d(scan) / "sections.json").read_text())
    xrefs = json.loads((d(scan) / "xrefs.json").read_text())
    pages = len({r["page"] for r in records})
    body = [r for r in records if r["region"] == "body" and r["class"] != "head"]
    cls = Counter(r["class"] for r in body)
    # section order: each head should follow the previous one in decimal order
    order_breaks = [(a["sec"], b["sec"], b["page"]) for a, b in zip(sections, sections[1:])
                    if sec_key(b["sec"]) <= sec_key(a["sec"])]
    known = {s["sec"] for s in sections}
    def resolves(r: str) -> bool:
        return r in known or any(k.startswith(r) and k.split(".")[0] == r.split(".")[0] for k in known)
    unresolved = [x for x in xrefs if not resolves(x["ref"])]
    val = validate(scan, records)

    lines = [f"# First pass: scan `{scan}`", "",
             f"<!-- generated by pipeline/firstpass.py report; statistics only, no page text -->", "",
             f"- PDF pages with text: {pages}; body starts at PDF page {body_start(scan)}, index at PDF page {index_start(scan)}",
             f"- Body lines (excluding running heads): {len(body)}",
             *(f"  - {c}: {n} ({n / len(body):.1%})" for c, n in cls.most_common()),
             f"- Section heads found: {len(sections)}; first {sections[0]['sec'] if sections else '-'}, "
             f"last {sections[-1]['sec'] if sections else '-'}",
             f"- Places where the section order goes backwards (OCR misreads or missed heads): {len(order_breaks)}",
             f"- Cross-reference candidates: {len(xrefs)}; not matching any section head found: {len(unresolved)}",
             ""]
    if val:
        lines += ["## Check against the pilot (9 body pages; reference = zoomed Opus 5.5 reading)", "",
                  "| line class | lines paired | character error rate |", "|---|---|---|",
                  *(f"| {c} | {v['lines']} | {v['cer']:.2%} |" for c, v in sorted(val.items())), ""]
    lines += ["## First section-order breaks", "", *(f"- {a} then {b} (p{pg})" for a, b, pg in order_breaks[:15]), ""]
    out = ROOT / "reports" / f"firstpass-{scan}.md"
    out.write_text("\n".join(lines))
    print("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["render", "ocr", "parse", "report", "all"])
    ap.add_argument("--scan", default="1961")
    a = ap.parse_args()
    steps = ["render", "ocr", "parse", "report"] if a.step == "all" else [a.step]
    for s in steps:
        globals()[s](a.scan)


if __name__ == "__main__":
    main()
