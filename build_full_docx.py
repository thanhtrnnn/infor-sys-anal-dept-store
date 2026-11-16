#!/usr/bin/env python3
"""Build the final report: v5 content regrouped into the four parts the course asks for, plus everything else.

Input : build/v5_vp-images.docx (v5 content with the Visual Paradigm images, from build_docx.py --vp)
        source/vp_images/*.png (figures of v1-v3 that later versions replaced)
        screenshots/app/*.png (screens of the running app), screenshots/editor-*.png (project tree in VS Code)
        prompts_appendix.json (prompts used, for Phụ lục C; kept local, not in git)
Output: 34_B23DCAT280_v8_2026-11-15_ban-cuoi.docx (cover page, A4, page numbers)
        = PHẦN I Đặc tả (1-4, 5.1-5.6, 6.1-6.5) · PHẦN II Phân tích (5.7-5.10, 6.6-6.9) · PHẦN III Thiết kế (7)
          · PHẦN IV Lập trình (8 + 8.4 screens, 8.5 project tree, 8.6 GitHub) + table of contents
          + Phụ lục A (version history) + Phụ lục B (replaced figures) + Phụ lục C (prompts and how they were used)

Run: uv run --no-project --with python-docx --with pillow python3 build_full_docx.py
"""
import copy
import json
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph
from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "build" / "v5_vp-images.docx"  # python3 build_docx.py --vp
OUT = ROOT / "34_B23DCAT280_v8_2026-11-15_ban-cuoi.docx"
LOGO = ROOT / "assets" / "ptit-logo.png"
SHOTS = ROOT / "screenshots"
PROMPTS = ROOT / "prompts_appendix.json"
GITHUB = "https://github.com/thanhtrnnn/infor-sys-anal-dept-store"
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
     "thử 26/26. Bản nộp Thiết kế 3 (toàn bộ pha thiết kế)."],
    ["v6", "27/10/2026", "TXTHANH\n34_B23DCAT280_v6_2026-10-27_tong-hop.docx",
     "Bản tổng hợp: nội dung v5, mục lục, lịch sử phiên bản (phụ lục A) và các hình của phiên bản trước đã được "
     "thay thế (phụ lục B)."],
    ["v7", "14/11/2026", "TXTHANH\n34_B23DCAT280_v7_2026-11-14_ban-cuoi.docx\n" + "github.com/thanhtrnnn/infor-sys-anal-dept-store",
     "Bản cuối: chia thành 4 phần Đặc tả / Phân tích / Thiết kế / Lập trình; thêm ảnh giao diện chạy thật (8.4), "
     "ảnh cấu trúc project trong editor (8.5), link mã nguồn GitHub (8.6), phụ lục C các prompt đã dùng."],
    ["v8", "15/11/2026", "TXTHANH\n34_B23DCAT280_v8_2026-11-15_ban-cuoi.docx\nvp/TXTHANH.vpp",
     "Mọi biểu đồ UML vẽ lại trong Visual Paradigm (build_vp.py) và xuất bằng VP Community Edition; trang bìa, khổ "
     "A4, đánh số trang; cây thư mục project gộp 2 cột Explorer trên một hàng (Hình 8.12); phụ lục C viết lại theo "
     "nhóm công việc; thêm phụ lục D tài liệu tham khảo."],
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
    t.autofit = False
    grid = t._tbl.tblGrid
    for c, gc in enumerate(grid.findall(qn("w:gridCol"))):
        gc.set(qn("w:w"), str(int(widths[c] * 567)))
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


def picture(path, caption, max_w=16.0):
    w, h = Image.open(path).size
    width = min(max_w, 20.0 * w / h)
    p = new_par(center=True)
    p.add_run().add_picture(str(path), width=Cm(width))
    new_par(text=caption, italic=True, center=True, size=10)


# ---------- 0. regroup v5 into the four parts ----------
def heading_text(e):
    if not e.tag.endswith("}p"):
        return None, ""
    p = Paragraph(e, d)
    return p.style.name, p.text.strip()


def part_heading(text, level=1):
    p = add_heading(text, level)
    body.remove(p._p)
    return p._p


kids = [k for k in body.iterchildren() if not k.tag.endswith("}sectPr")]
starts = {}
for i, k in enumerate(kids):
    style, text = heading_text(k)
    for key in ("1.", "5.", "5.7.", "6.", "6.6.", "7.", "8."):
        if style in ("Heading 1", "Heading 2") and text.startswith(key + " "):
            starts[key] = i
order = ["1.", "5.", "5.7.", "6.", "6.6.", "7.", "8."]
cut = [starts[k] for k in order] + [len(kids)]
seg = {k: kids[cut[n]:cut[n + 1]] for n, k in enumerate(order)}
for k in kids[starts["1."]:]:
    body.remove(k)
sect = body.find(qn("w:sectPr"))


def put(elements):
    for e in elements:
        sect.addprevious(e)


put([part_heading("PHẦN I. ĐẶC TẢ")])
put(seg["1."] + seg["5."] + seg["6."])
put([page_break()._p, part_heading("PHẦN II. PHÂN TÍCH")])
put([part_heading("Phân tích module 1 - Customer tracks invoice (tiếp mục 5)")] + seg["5.7."])
put([part_heading("Phân tích module 2 - Sale staff approves orders + export (tiếp mục 6)")] + seg["6.6."])
put([page_break()._p, part_heading("PHẦN III. THIẾT KẾ")])
put(seg["7."])
put([page_break()._p, part_heading("PHẦN IV. LẬP TRÌNH")])
put(seg["8."])
# ---------- 0b. PHẦN IV additions: screens, project tree, GitHub ----------
APP = [
    ("01-gdLogin", "gdLogin.jsp - đăng nhập (nhân viên bán hàng lan / 123456)"),
    ("02-gdSaleHome", "gdSaleHome.jsp - trang chủ nhân viên bán hàng NV01 Hoàng Thị Lan"),
    ("03-gdOrderList", "gdOrderList.jsp - danh sách đơn chưa xuất (DH1024, DH1025, DH1026)"),
    ("04-gdOrderDetail-cho-duyet", "gdOrderDetail.jsp - chi tiết đơn DH1024 trạng thái Chờ duyệt, tồn kho 40/120/60"),
    ("05-gdOrderDetail-da-duyet", "Sau khi bấm Duyệt đơn: thông báo \"Duyệt đơn thành công\", trạng thái Đã duyệt"),
    ("06-gdDeliveryStaffList", "gdDeliveryStaffList.jsp - chọn nhân viên giao hàng GH03 Phạm Văn Dũng"),
    ("07-gdOrderDetail-da-xuat", "Sau khi lưu phân công và xác nhận xuất hàng: thông báo \"Xuất hàng thành công cho đơn "
     "DH1024\", trạng thái Đã xuất, tồn kho giảm còn 38/115/50"),
    ("08-gdInvoicePrint", "gdInvoicePrint.jsp - hóa đơn bán hàng HD1024 để in và giao cùng hàng"),
    ("09-gdCustomerHome", "gdCustomerHome.jsp - trang chủ khách hàng KH01 Nguyễn Văn An (an / 123456)"),
    ("10-gdInvoiceList", "gdInvoiceList.jsp - danh sách hóa đơn đã đặt, mới nhất trước"),
    ("11-gdInvoiceDetail", "gdInvoiceDetail.jsp - chi tiết hóa đơn HD1024 và trạng thái hiện tại Đã xuất"),
]
add_heading("8.4. Giao diện chương trình khi chạy", 2)
new_par(text="Các ảnh chụp từ ứng dụng chạy thật (Tomcat nhúng, dữ liệu mẫu sql/system_sample_data.sql), đi đúng hai "
             "kịch bản chuẩn: module 2 trước (NV01 duyệt, phân công GH03, xuất và in DH1024), sau đó module 1 (KH01 "
             "theo dõi hóa đơn HD1024 vừa xuất). Thông báo của các trang do*.jsp hiện bằng hộp thoại alert của trình "
             "duyệt, được ghi trong chú thích hình.")
add_heading("Module 2 - Sale staff approves orders + export", 3)
for n, (name, cap) in enumerate(APP, 1):
    if n == 9:
        add_heading("Module 1 - Customer tracks invoice", 3)
    picture(SHOTS / "app" / f"{name}.png", f"Hình 8.{n} - {cap}")
add_heading("8.5. Cấu trúc project trong editor", 2)
new_par(text="Project mở trong Visual Studio Code. Thư mục java/ theo bố cục của giáo trình: src/model (JavaBean thực "
             "thể), src/dao (lớp DAO cơ sở và các XxxDAO extends DAO), WebContent (trang gd*/do*.jsp chia theo actor: "
             "khachhang/, nhanvienbanhang/; WEB-INF/web.xml), test (unittest: kiểm thử DAO; webtest: chạy các trang JSP "
             "trong Tomcat nhúng; run: chương trình chạy thử). sql/ chứa lược đồ CSDL và dữ liệu mẫu, diagrams/ chứa mã "
             "PlantUML, project Visual Paradigm (vp/) và ảnh của mọi biểu đồ.")
picture(SHOTS / "editor-explorer-2col.png", "Hình 8.12 - Cây thư mục trong Explorer của VS Code: bên trái java/src "
        "(dao, model) và java/test; bên phải java/WebContent (khachhang, nhanvienbanhang, WEB-INF)", max_w=13.0)
add_heading("8.6. Mã nguồn trên GitHub", 2)
p = new_par(text="Link source code: ")
r = p.add_run(GITHUB)
r.bold = True
new_par(text="Repository gồm mã Java/JSP (java/), CSDL (sql/), mã PlantUML và ảnh biểu đồ (diagrams/, puml_nop_bai/), "
             "ảnh giao diện (screenshots/) và các script:")
for line in ["python3 run_app.py - biên dịch và chạy ứng dụng tại http://localhost:8080/gdLogin.jsp (cần Java 17+, "
             "không cần cài MySQL/Tomcat: dùng SQLite + Tomcat nhúng với dữ liệu mẫu)",
             "python3 verify.py - kiểm tra CSDL, biên dịch, chạy 26 ca kiểm thử (23 ca DAO + 3 ca luồng web), kiểm tra "
             "cú pháp PlantUML. Kết quả ngày 16/11/2026: 26/26 ca đạt, VERIFIED",
             "python3 build_puml_nop_bai.py - sinh mã PlantUML độc lập (không !include) để nộp vào form",
             "python3 build_vp.py - vẽ lại mọi biểu đồ trong Visual Paradigm (qua plugin VP MCP) và xuất ảnh "
             "diagrams/out/vp/*.png dùng trong báo cáo"]:
    new_par("List Bullet", line)

page_break()
add_heading("Phụ lục A. Lịch sử phiên bản", 1)
new_par(text="Các phiên bản của báo cáo, từ bản đầu tiên trong cnpm-hrm đến bản tổng hợp này. Tên tệp đã được đổi để "
             "phân biệt; các bản dựng trung gian trong TXTHANH (28/09 - 09/10/2026) được ghi đè khi dựng lại nên không "
             "còn tệp riêng, nội dung của chúng nằm trong v4.")
table([["Phiên bản", "Ngày", "Nguồn / tệp", "Nội dung và thay đổi chính"]] + VERSIONS, [1.6, 2.0, 5.4, 8.0])
new_par()
add_heading("Phụ lục B. Hình của các phiên bản trước", 1)
new_par(text="Các hình dưới đây đã được thay thế ở phiên bản sau; giữ lại để đối chiếu. Bốn hình vẽ bằng Visual Paradigm "
             "(B.4 - B.7) được dựng lại từ dự án b23dcat280.vpp và xuất bằng Visual Paradigm Community Edition, giữ nguyên "
             "nội dung của phiên bản cũ; ba hình use case (B.1 - B.3) vẽ bằng PlantUML.")
CE_OLD = ROOT / "diagrams" / "out" / "vp_old_final"
for n, (name, title, replaced) in enumerate(OLD_FIGURES, 1):
    src = CE_OLD / name if (CE_OLD / name).exists() else OLD_FIGS / name
    picture(src, f"Hình B.{n} - {title}. Đã thay bằng: {replaced}")

page_break()
add_heading("Phụ lục C. Prompt sử dụng trong quá trình làm bài", 1)
prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))
new_par("List Bullet", "Công cụ: " + prompts["tool"])
new_par("List Bullet", "Cách đọc cột \"Cách sử dụng kết quả\":")
for line in prompts["legend"]:
    new_par("List Bullet 2", line)
for g, group in enumerate(prompts["groups"], 1):
    add_heading(f"C.{g}. {group['title']}", 2)
    table([["#", "Prompt", "Kết quả", "Cách sử dụng kết quả"]]
          + [[f"{g}.{i}", *row] for i, row in enumerate(group["rows"], 1)],
          [1.0, 6.6, 4.4, 4.0])
    new_par()
add_heading("Phụ lục D. Tài liệu tham khảo", 1)
for i, (ref, url) in enumerate(prompts["references"], 1):
    p = new_par(text=f"[{i}] {ref}" + (" " if url else ""))
    if url:
        p.add_run(url).italic = True

# ---------- 1b. headings that named the old drawing tool ----------
RENAME = {"4.1. PlantUML - Use case tổng quan": "4.1. Biểu đồ use case tổng quan",
          "5.5. PlantUML - Customer tracks invoice": "5.5. Biểu đồ use case chi tiết - Customer tracks invoice",
          "6.4. PlantUML - Sale staff approves order + export":
              "6.4. Biểu đồ use case chi tiết - Sale staff approves order + export"}
for p in d.paragraphs:
    if p.text.strip() in RENAME:
        new = RENAME[p.text.strip()]
        for r in p.runs[1:]:
            r._r.getparent().remove(r._r)
        p.runs[0].text = new

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


# ---------- 4. layout: A4, Times New Roman 13, page numbers, cover page ----------
from docx.enum.section import WD_SECTION  # noqa: E402
from docx.shared import Pt as _Pt  # noqa: E402

for name in ("normal", "List Bullet", "List Bullet 2"):
    st = d.styles[name]
    st.font.name = "Times New Roman"
    st.font.size = _Pt(13)
    st.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), "Times New Roman")
    st.paragraph_format.space_after = _Pt(4)
    st.paragraph_format.line_spacing = 1.2
for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 13)):
    st = d.styles[name]
    st.font.name = "Times New Roman"
    st.font.size = _Pt(size)
    st.font.bold = True
    st.paragraph_format.space_before = _Pt(12 if name == "Heading 1" else 8)
    st.paragraph_format.space_after = _Pt(6)
    st.paragraph_format.keep_with_next = True
for p in d.paragraphs:  # part titles centred
    if p.style.name == "Heading 1" and p.text.startswith(("PHẦN ", "ĐỀ BÀI", "Phụ lục")):
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif p.style.name == "normal" and len(p.text) > 120 and p.alignment is None:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

main = d.sections[0]
main.page_width, main.page_height = Cm(21.0), Cm(29.7)
main.left_margin, main.right_margin = Cm(3.0), Cm(2.0)
main.top_margin, main.bottom_margin = Cm(2.0), Cm(2.0)
pg = main._sectPr.find(qn("w:pgNumType"))
if pg is None:
    pg = el("w:pgNumType")
    main._sectPr.append(pg)
pg.set(qn("w:start"), "1")
fp = main.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
for extra in main.footer.paragraphs[1:]:
    extra._p.getparent().remove(extra._p)
for child in list(fp._p):  # the v3 footer already holds a PAGE field: start from an empty paragraph
    if child.tag != qn("w:pPr"):
        fp._p.remove(child)
for k in ("begin", None, "separate", "end"):
    fp._p.append(fld(k) if k else instr(" PAGE "))

# cover = own section (no page number, double page border), inserted before the exam-question page
cover = []


def cpar(text="", size=13, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=0, indent=None):
    p = d.add_paragraph(style="normal")
    p.alignment = align
    p.paragraph_format.space_before, p.paragraph_format.space_after = _Pt(before), _Pt(after)
    p.paragraph_format.line_spacing = 1.15
    if indent is not None:
        p.paragraph_format.left_indent = Cm(indent)
    if text:
        r = p.add_run(text)
        r.bold, r.italic, r.font.size = bold or None, italic or None, _Pt(size)
    cover.append(p)
    return p


cpar("HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG", 13, bold=True, before=24)
cpar("KHOA CÔNG NGHỆ THÔNG TIN 1", 13, bold=True, before=6)
cpar("──────────────", 13, after=24)
logo = cpar(after=30)
logo.add_run().add_picture(str(LOGO), width=Cm(3.6))
cpar("BÁO CÁO", 14, bold=True, after=8)
cpar("PHÂN TÍCH THIẾT KẾ", 22, bold=True)
cpar("HỆ THỐNG THÔNG TIN", 22, bold=True, after=14)
cpar("Hệ thống quản lí cửa hàng bách hóa trực tuyến", 14, italic=True)
cpar("(Online Department Store Management System)", 13, italic=True, after=20)
cpar("Đề tài: 34", 16, bold=True, after=30)
INFO = [("Giảng viên hướng dẫn", "Đỗ Thị Bích Ngọc"),
        ("Họ và tên sinh viên", "Trần Xuân Thành"),
        ("Mã sinh viên", "B23DCAT280"),
        ("Lớp", "CLC N1")]
for k, v in INFO:
    p = cpar(align=WD_ALIGN_PARAGRAPH.LEFT, indent=1.8, after=2)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(6.3))
    p.add_run(f"{k}\t: ").bold = True
    p.add_run(v).bold = True
cpar("Hà Nội – 2026", 13, bold=True, italic=True, before=70)

end = d.add_paragraph()
cover_sect = el("w:sectPr")
for tag, attrs in (("w:pgSz", {"w:w": "11906", "w:h": "16838"}),
                   ("w:pgMar", {"w:top": "1134", "w:right": "1134", "w:bottom": "1134", "w:left": "1418",
                                "w:header": "709", "w:footer": "709", "w:gutter": "0"})):
    cover_sect.append(el(tag, **attrs))
borders = el("w:pgBorders", **{"w:offsetFrom": "page"})
for side in ("top", "left", "bottom", "right"):
    borders.append(el(f"w:{side}", **{"w:val": "thinThickSmallGap", "w:sz": "24", "w:space": "24",
                                       "w:color": "1F3864"}))
cover_sect.append(borders)
end._p.get_or_add_pPr().append(cover_sect)
cover.append(end)
first = body[0]
for p in cover:
    first.addprevious(p._p)

def is_par_el(e):
    return e is not None and e.tag == qn("w:p")


def par_text_el(e):
    return "".join(t.text or "" for t in e.iter(qn("w:t"))).strip()


# ---------- 4b. the exam question fits on one page ----------
question = next(e for e in body.iterchildren() if is_par_el(e) and par_text_el(e) == "ĐỀ BÀI")
e = question
while e is not None:
    if is_par_el(e) and e.findall(".//" + qn("w:br")) and not par_text_el(e):
        break  # the page break before the table of contents ends the question page
    if is_par_el(e) and e is not question:
        para = Paragraph(e, d)
        para.paragraph_format.space_after = _Pt(2)
        para.paragraph_format.line_spacing = 1.0
        for r in para.runs:
            r.font.size = _Pt(11)
    e = e.getnext()


# ---------- 5. wide diagrams get their own landscape page ----------
VPO = ROOT / "diagrams" / "out" / "vp"
SPL = ROOT / "diagrams" / "out" / "vp_split"
SEQ_A, SEQ_D = "x3-sequence-analysis-approve-export", "q3c-4-sequence-design-approve-export"
LANDSCAPE = [  # caption prefix, [(png, caption suffix)], tallest picture (cm); the page is 25.7 x 17 cm
    ("Hình 6.3 - ", [(SPL / f"{SEQ_A}_1.png", " - phần 1/2, bước 1 - 29"),
                     (SPL / f"{SEQ_A}_2.png", " - phần 2/2, bước 30 - 51")], 14.2),
    ("Hình 6.6 - ", [(VPO / "q3a-4-communication-approve-export.png", "")], 11.0),
    ("Hình 7.4.7 - ", [(VPO / "q3c-2-activity-approve-export.png", "")], 12.0),
    ("Hình 7.4.8 - ", [(SPL / f"{SEQ_D}_1.png", " - phần 1/2, bước 1 - 42"),
                       (SPL / f"{SEQ_D}_2.png", " - phần 2/2, bước 43 - 86")], 14.2),
    ("Hình 7.5 - ", [(VPO / "q5a-package.png", "")], 11.0),
    ("Hình 7.6 - ", [(VPO / "q5b-deployment.png", "")], 9.5),
]
LAND_W = 25.5


def is_par(e):
    return e is not None and e.tag == qn("w:p")


def par_text(e):
    return "".join(t.text or "" for t in e.iter(qn("w:t"))).strip()


def par_style(e):
    st = e.find(qn("w:pPr") + "/" + qn("w:pStyle"))
    return st.get(qn("w:val")) if st is not None else ""


def fill_picture(par_el, path, max_h):
    para = Paragraph(par_el, d)
    for r in list(para.runs):
        r._r.getparent().remove(r._r)
    w, h = Image.open(path).size
    width = min(LAND_W, max_h * w / h)
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.add_run().add_picture(str(path), width=Cm(width))


def set_caption(par_el, text):
    para = Paragraph(par_el, d)
    para.runs[0].text = text
    for r in para.runs[1:]:
        r._r.getparent().remove(r._r)


def section_par(sect):
    p = el("w:p")
    ppr = el("w:pPr")
    ppr.append(el("w:spacing", **{"w:before": "0", "w:after": "0", "w:line": "20", "w:lineRule": "exact"}))
    ppr.append(sect)
    p.append(ppr)
    return p


def sect_copy(landscape=False, numbering_start=False):
    s = copy.deepcopy(body.find(qn("w:sectPr")))
    num = s.find(qn("w:pgNumType"))
    if num is not None and not numbering_start:
        num.attrib.pop(qn("w:start"), None)
    if landscape:
        sz = s.find(qn("w:pgSz"))
        sz.set(qn("w:w"), "16838")
        sz.set(qn("w:h"), "11906")
        sz.set(qn("w:orient"), "landscape")
        mar = s.find(qn("w:pgMar"))
        for side in ("top", "bottom", "left", "right"):
            mar.set(qn(f"w:{side}"), "1134")
    return s


targets = []
for prefix, parts, max_h in LANDSCAPE:
    cap = next(e for e in body.iterchildren() if is_par(e) and par_text(e).startswith(prefix))
    pic = cap.getprevious()
    assert pic.findall(".//" + qn("w:drawing")), prefix
    start = pic
    while par_style(start) not in ("Heading2", "Heading3"):  # the section heading opens the page
        start = start.getprevious()
    targets.append([prefix, parts, max_h, start, pic, cap])

for prefix, parts, max_h, start, pic, cap in targets:  # fill the pictures; a split figure gets a second page
    caption = par_text(cap)
    fill_picture(pic, parts[0][0], max_h)
    set_caption(cap, caption + parts[0][1])
    last = cap
    for path, suffix in parts[1:]:
        pic2 = copy.deepcopy(pic)
        cap2 = copy.deepcopy(cap)
        last.addnext(pic2)
        pic2.addnext(cap2)
        fill_picture(pic2, path, max_h)
        set_caption(cap2, caption + suffix)
        Paragraph(pic2, d).paragraph_format.page_break_before = True
        last = cap2
    targets[targets.index([prefix, parts, max_h, start, pic, cap])].append(last)

groups = []  # consecutive figures share one landscape section
for t in targets:
    if groups and groups[-1][-1][6].getnext() is t[3]:
        groups[-1].append(t)
        Paragraph(t[3], d).paragraph_format.page_break_before = True
    else:
        groups.append([t])
for n, g in enumerate(groups):
    g[0][3].addprevious(section_par(sect_copy(numbering_start=n == 0)))  # ends the portrait section before
    end_par = section_par(sect_copy(landscape=True))
    g[-1][6].addnext(end_par)  # ends the landscape section
    nxt = end_par.getnext()
    while is_par(nxt) and not par_text(nxt) and (nxt.findall(".//" + qn("w:br")) or not nxt.findall(".//" + qn("w:drawing"))):
        gone, nxt = nxt, nxt.getnext()  # the section break already starts a new page: drop empty / page-break paragraphs
        gone.getparent().remove(gone)
body.find(qn("w:sectPr")).find(qn("w:pgNumType")).attrib.pop(qn("w:start"), None)

d.core_properties.title = "B23DCAT280 - Hệ thống quản lí cửa hàng bách hóa trực tuyến (bản cuối)"
d.save(OUT)
print(f"wrote {OUT.name}: {len(headings)} TOC entries")
