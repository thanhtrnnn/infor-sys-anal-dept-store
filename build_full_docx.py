#!/usr/bin/env python3
"""Build the consolidated report: every version collected into one document.

Input : 34_B23DCAT280_v5_2026-10-26_day-du.docx (latest full report, from build_docx.py)
        source/vp_images/*.png (figures of v1-v3 that later versions replaced)
Output: 34_B23DCAT280_v6_2026-10-27_tong-hop.docx
        = v5 + table of contents (Word TOC field, links to heading bookmarks) + Phụ lục A (version history)
          + Phụ lục B (figures replaced in later versions)

Run: uv run --no-project --with python-docx --with pillow python3 build_full_docx.py
"""
import copy
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph
from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "34_B23DCAT280_v5_2026-10-26_day-du.docx"
OUT = ROOT / "34_B23DCAT280_v6_2026-10-27_tong-hop.docx"
OLD_FIGS = ROOT / "source" / "vp_images"

VERSIONS = [
    ["v1", "21/09/2026", "cnpm-hrm, commit a705111\nversions/34_B23DCAT280_v1_2026-09-21_module2-PlantUML.docx",
     "Mục 1-4 (từ khóa, mô tả hệ thống, quy tắc nghiệp vụ, use case tổng quan); module 1 (đặc tả, luồng sự kiện, "
     "phân rã UC); module 2: kịch bản chuẩn có dữ liệu mẫu, trích lớp thực thể, lớp phân tích, biểu đồ trạng thái, "
     "kịch bản phiên bản 2 (51 bước). Biểu đồ module 2 ở dạng mã PlantUML."],
    ["v2", "21/09/2026", "cnpm-hrm, commit 104ba2a\nversions/34_B23DCAT280_v2_2026-09-21_hinh-VP.docx",
     "Thay mã PlantUML bằng 3 hình vẽ trong Visual Paradigm: biểu đồ thực thể, lớp phân tích, tuần tự 51 bước."],
    ["v3", "21/09/2026", "cnpm-hrm, commit 4545910 (bản hiện tại của cnpm-hrm)\n"
     "source/34_B23DCAT280_v3_2026-09-21_cnpm-hrm-goc.docx",
     "Thêm biểu đồ trạng thái đơn hàng vẽ bằng Visual Paradigm (mục 6.8)."],
    ["v4", "12/10/2026", "TXTHANH\nversions/34_B23DCAT280_v4_2026-10-12_phan-tich-thiet-ke.docx\n"
     "submission_ready/Thiet_ke_1, Thiet_ke_2",
     "Chuyển sang TXTHANH; thêm trang đề bài; phân tích đầy đủ module 1 (5.6-5.10); sửa phân tích module 2 (bội số "
     "0..1, thuộc tính area, bỏ Invoice.status, nút subBack, trạng thái); mọi hình vẽ lại bằng PlantUML; chương 7 "
     "Thiết kế (7.1-7.4). Bản nộp Thiết kế 1 (7.1-7.2, giao diện, lớp module) và Thiết kế 2 (hoạt động, kịch bản "
     "v3, tuần tự)."],
    ["v5", "26/10/2026", "TXTHANH\n34_B23DCAT280_v5_2026-10-26_day-du.docx\nsubmission_ready/Thiet_ke_3",
     "Use case phân rã theo giao diện, đăng nhập theo actor, «extend»; thực thể pha phân tích bỏ id, thêm kế thừa "
     "Member/Staff; CSDL hai module; 7.5 biểu đồ gói, 7.6 biểu đồ triển khai; chương 8 Cài đặt (câu 4b) và kiểm "
     "thử 25/25. Bản nộp Thiết kế 3 (toàn bộ pha thiết kế)."],
    ["v6", "27/10/2026", "TXTHANH\n34_B23DCAT280_v6_2026-10-27_tong-hop.docx",
     "Bản tổng hợp: nội dung v5, mục lục, lịch sử phiên bản (phụ lục A) và các hình của phiên bản trước đã được "
     "thay thế (phụ lục B)."],
]

OLD_FIGURES = [
    ("uc_overview.png", "Use case tổng quan (v1-v3, PlantUML)", "Hình mục 4.1 của bản này"),
    ("uc_track_invoice.png", "Use case chi tiết module 1 (v1-v3)",
     "Hình mục 5.5: bỏ View Current Invoice Status 0, thêm Customer Login 0 và «extend»"),
    ("uc_approve_export.png", "Use case chi tiết module 2 (v1-v3)",
     "Hình mục 6.4: phân rã theo giao diện, bỏ Approve / Pack / Export / Check Inventory..."),
    ("class_entity.png", "Biểu đồ thực thể module 2 (v2-v3, Visual Paradigm)",
     "Hình 6.1: bội số 0..1, kế thừa Member / Staff, không còn id"),
    ("class_analysis_bce.png", "Biểu đồ lớp phân tích module 2 (v2-v3, Visual Paradigm)",
     "Hình 6.2: giữ quan hệ thực thể, thêm subBack"),
    ("sequence_analysis.png", "Biểu đồ tuần tự phân tích 51 bước (v2-v3, Visual Paradigm)", "Hình 6.3"),
    ("state_order.png", "Biểu đồ trạng thái đơn hàng (v3, Visual Paradigm)",
     "Hình 6.4: bỏ trạng thái ReadyForExport; thêm Hình 6.5 dạng luồng giao diện"),
]

d = docx.Document(SRC)
body = d.element.body


# ---------- helpers ----------
def new_par(style="normal", text="", bold=False, italic=False, center=False, size=None):
    p = d.add_paragraph(style=style)
    if text:
        r = p.add_run(text)
        r.bold = bold or None
        r.italic = italic or None
        if size:
            r.font.size = Pt(size)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p


def page_break():
    p = d.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)
    return p


def el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(k), v)
    return e


def fld(kind):
    r = el("w:r")
    r.append(el("w:fldChar", **{"w:fldCharType": kind}))
    return r


def instr(text):
    r = el("w:r")
    t = el("w:instrText", **{"xml:space": "preserve"})
    t.text = text
    r.append(t)
    return r


# ---------- 1. appendices (before collecting headings, so they are in the TOC) ----------
def add_heading(text, level):
    p = d.add_paragraph(style=f"Heading {level}")
    p.add_run(text)
    return p


def table(rows, widths):
    t = d.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = t.cell(r, c)
            cell.width = Cm(widths[c])
            cell.text = ""
            for k, line in enumerate(str(value).split("\n")):
                para = cell.paragraphs[0] if k == 0 else cell.add_paragraph()
                run = para.add_run(line)
                run.bold = True if r == 0 else None
                run.font.size = Pt(9 if r else 10)
    return t


def picture(path, caption):
    w, h = Image.open(path).size
    width = min(16.0, 20.0 * w / h)
    p = new_par(center=True)
    p.add_run().add_picture(str(path), width=Cm(width))
    new_par(text=caption, italic=True, center=True, size=10)


page_break()
add_heading("Phụ lục A. Lịch sử phiên bản", 1)
new_par(text="Các phiên bản của báo cáo, từ bản đầu tiên trong cnpm-hrm đến bản tổng hợp này. Tên tệp đã được đổi để "
             "phân biệt; các bản dựng trung gian trong TXTHANH (28/09 - 09/10/2026) được ghi đè khi dựng lại nên không "
             "còn tệp riêng, nội dung của chúng nằm trong v4.")
table([["Phiên bản", "Ngày", "Nguồn / tệp", "Nội dung và thay đổi chính"]] + VERSIONS, [1.6, 2.0, 5.4, 8.0])
new_par()
add_heading("Phụ lục B. Hình của các phiên bản trước", 1)
new_par(text="Các hình dưới đây đã được thay thế ở phiên bản sau; giữ lại để đối chiếu. Hình vẽ bằng Visual Paradigm "
             "bản dùng thử nên có hình mờ \"evaluation copy\".")
for n, (name, title, replaced) in enumerate(OLD_FIGURES, 1):
    picture(OLD_FIGS / name, f"Hình B.{n} - {title}. Đã thay bằng: {replaced}")

# ---------- 2. bookmarks on every heading (level 1-3) ----------
headings = []
for n, p in enumerate(d.paragraphs):
    name = p.style.name
    if name in ("Heading 1", "Heading 2", "Heading 3") and p.text.strip() and p.text.strip() != "ĐỀ BÀI":
        mark = f"_Toc{100000 + n}"
        p._p.insert(1 if p._p.pPr is not None else 0, el("w:bookmarkStart", **{"w:id": str(n), "w:name": mark}))
        p._p.append(el("w:bookmarkEnd", **{"w:id": str(n)}))
        headings.append((int(name[-1]), p.text.strip(), mark))


# ---------- 3. table of contents after the exam-question page ----------
def toc_block(entries):
    """A Word TOC field inside a 'Table of Contents' content control, with cached hyperlinked entries."""
    sdt = el("w:sdt")
    pr = el("w:sdtPr")
    part = el("w:docPartObj")
    part.append(el("w:docPartGallery", **{"w:val": "Table of Contents"}))
    part.append(el("w:docPartUnique"))
    pr.append(part)
    sdt.append(pr)
    content = el("w:sdtContent")
    title = new_par("TOC Heading", "MỤC LỤC", bold=True)
    content.append(title._p)
    for i, (level, text, mark) in enumerate(entries):
        p = d.add_paragraph(style="normal")
        p.paragraph_format.left_indent = Cm(0.6 * (level - 1))
        p.paragraph_format.space_after = Pt(0)
        if i == 0:
            p._p.append(fld("begin"))
            p._p.append(instr(' TOC \\o "1-3" \\h \\z \\u '))
            p._p.append(fld("separate"))
        link = el("w:hyperlink", **{"w:anchor": mark, "w:history": "1"})
        r = el("w:r")
        if level == 1:
            rpr = el("w:rPr")
            rpr.append(el("w:b"))
            r.append(rpr)
        t = el("w:t", **{"xml:space": "preserve"})
        t.text = text
        r.append(t)
        link.append(r)
        p._p.append(link)
        if i == len(entries) - 1:
            p._p.append(fld("end"))
        content.append(p._p)
    sdt.append(content)
    return sdt


first_break = next(p for p in d.paragraphs if p._p.xpath(".//w:br[@w:type='page']"))
toc = toc_block(headings)
first_break._p.addnext(toc)
toc.addnext(page_break()._p)
settings = d.settings.element
settings.append(el("w:updateFields", **{"w:val": "true"}))  # Word refreshes page numbers on open


d.core_properties.title = "B23DCAT280 - Hệ thống quản lí cửa hàng bách hóa trực tuyến (bản tổng hợp)"
d.save(OUT)
print(f"wrote {OUT.name}: {len(headings)} TOC entries")
