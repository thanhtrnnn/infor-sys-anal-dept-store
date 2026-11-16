#!/usr/bin/env python3
"""Page numbers for the table of contents: read the converted PDF, find each heading in order, and write
build/toc_pages.json (one printed page number per heading, same order as the TOC). build_full_docx.py reads it.
Usage: python3 make_toc_pages.py <docx> <pdf>"""
import json
import re
import subprocess
import sys
from pathlib import Path

from docx import Document

docx_path, pdf_path = sys.argv[1:3]
ROOT = Path(__file__).resolve().parent
heads = [p.text.strip() for p in Document(docx_path).paragraphs
         if p.style.name in ("Heading 1", "Heading 2", "Heading 3") and p.text.strip() and p.text.strip() != "ĐỀ BÀI"]
n_pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True).stdout).group(1))
pages = []
for i in range(1, n_pages + 1):
    text = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), pdf_path, "-"], capture_output=True, text=True).stdout
    pages.append(re.sub(r"\s+", " ", text))
norm = lambda s: re.sub(r"\s+", " ", s).strip()
first_body = next(i for i, t in enumerate(pages) if t.startswith("PHẦN I") or "PHẦN I. ĐẶC TẢ PHÂN TÍCH" in t[:80] or "PHÂN TÍCH YÊU CẦU" in t[:60])
result, cur = [], first_body
for h in heads:
    key = norm(h)[:60]
    for j in range(cur, n_pages):
        if key in pages[j]:
            cur = j
            break
    else:
        print("not found:", h)
    result.append(cur)  # pdf page index (0-based); page 2 prints as 1, so the label is index (0-based)
json.dump(result, open(ROOT / "build" / "toc_pages.json", "w"))
print(len(result), "headings; first", result[:3], "last", result[-3:])
