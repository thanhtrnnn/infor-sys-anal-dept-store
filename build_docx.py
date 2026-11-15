#!/usr/bin/env python3
"""Rebuild the v5 report (34_B23DCAT280_v5_2026-10-26_day-du.docx) with the full analysis and design.

Input : source/34_B23DCAT280_v3_2026-09-21_cnpm-hrm-goc.docx (untouched report from cnpm-hrm) + diagrams/out/png/*.png
Output: 34_B23DCAT280_v5_2026-10-26_day-du.docx (+ submission_ready/Thiet_ke_3)

Changes to the original report:
- Use case images (4.1, 5.5, 6.4) and module 2 figures (6.1-6.4) are replaced by the PlantUML exports.
- Module 1 gets the full analysis: 5.6 standard scenario with sample data, 5.7 entity extraction,
  5.8 analysis class diagram, 5.9 screen-flow state diagram, 5.10 scenario v2 + communication + sequence.
- Module 2 corrections: multiplicities 0..1, DeliveryStaff.area, no Invoice.status, subBack buttons,
  state constraints without ReadyForExport, screen-flow state diagram (6.8) and communication diagram (6.9.4).
- Analysis entities use business codes (no id in the analysis phase) and the Member/Staff inheritance.
- First page: the exam question (question.md). New chapter 7 "Thiết kế" (textbook BG HP TTTN 2 CNPM 2020, ch. 4):
  system design entity classes, system database, and for each module the UI design, design class diagram,
  activity diagram, scenario v3 and design sequence diagram.

Run: uv run --no-project --with python-docx --with pillow python3 build_docx.py
(re-run after `python3 export_diagrams.py -f png` whenever a diagram changes)
"""
import copy
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt
from docx.table import Table
from docx.text.paragraph import Paragraph
from PIL import Image

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "diagrams"))
import generate  # noqa: E402  scenario v3 data

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "source" / "34_B23DCAT280_v3_2026-09-21_cnpm-hrm-goc.docx"
USE_VP = "--vp" in sys.argv  # Visual Paradigm images: intermediate input of build_full_docx.py (v8)
OUT = ROOT / ("build/v5_vp-images.docx" if USE_VP else "34_B23DCAT280_v5_2026-10-26_day-du.docx")
PNG = ROOT / "diagrams" / "out" / "png"
VP_PNG = ROOT / "diagrams" / "out" / "vp"  # Visual Paradigm CE exports (build_vp.py); preferred when present
MAX_W, MAX_H = (16.0, 22.0) if "--vp" in sys.argv else (16.5, 21.0)  # cm; v8 is A4 with 3 cm / 2 cm side margins

d = docx.Document(SRC)
body = list(d.element.body.iterchildren())


def P(i):
    return Paragraph(body[i], d)


def T(i):
    return Table(body[i], d)


def expect(i, text):
    got = P(i).text if body[i].tag.endswith("}p") else T(i).cell(0, 0).text
    assert got.startswith(text), f"body[{i}] = {got!r}, expected {text!r}"


# ---------- element builders (created at the end of the body, then moved) ----------
def para(text="", style="normal", bold_prefix=None, italic=False, center=False):
    p = d.add_paragraph(style=style)
    if bold_prefix:
        p.add_run(bold_prefix).bold = True
    if text:
        p.add_run(text).italic = italic or None
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p._p


def heading(text, level):
    return para(text, style=f"Heading {level}")


def bullet(text):
    return para(text, style="List Bullet")


def table(rows):
    t = d.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = t.cell(r, c)
            cell.text = ""
            cell.paragraphs[0].add_run(str(value)).bold = True if r == 0 else None
    return [t._tbl, para()]


def picture_run(paragraph, name):
    path = VP_PNG / f"{name}.png"
    if not (USE_VP and path.exists()):
        path = PNG / f"{name}.png"
    w, h = Image.open(path).size
    width = MAX_W
    if width * h / w > MAX_H:
        width = MAX_H * w / h
    paragraph.add_run().add_picture(str(path), width=Cm(width))


def figure(name, caption):
    p = d.add_paragraph(style="normal")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    picture_run(p, name)
    cap = d.add_paragraph(style="normal")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(caption)
    run.italic = True
    run.font.size = Pt(10)
    return [p._p, cap._p]


def insert_after(anchor, elements):
    for el in flatten(elements):
        anchor.addnext(el)
        anchor = el
    return anchor


def flatten(items):
    for item in items:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item


def replace_picture(i, name):
    p = P(i)
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    picture_run(p, name)


def set_text(paragraph, text):
    runs = paragraph.runs
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def set_cell(t, r, c, text):
    cell = t.cell(r, c)
    set_text(cell.paragraphs[0], text)


# ---------- sanity checks: the anchors are where the original report has them ----------
for i, text in [(226, "4.1."), (245, "5.5."), (247, "6. Use case"), (269, "6.4."), (336, "Một SaleStaff"),
                (337, "Một DeliveryStaff"), (338, "Một Order chứa"), (345, "6.6.5."), (347, "Hình 6.1"),
                (350, "Lớp Boundary"), (365, "6.7.4."), (367, "Hình 6.2"), (368, "6.8."), (369, "Đối tượng"),
                (371, "Hình 6.4"), (373, "Ràng buộc"), (427, "6.9.2."), (429, "Hình 6.3"), (450, "Nhân viên")]:
    expect(i, text)
first_element = body[0]  # title of the original report
anchor_m1 = body[246]      # 5.5 use case image: module 1 analysis goes after it
anchor_state = body[373]   # 6.8 constraint table
anchor_end = body[450]     # last paragraph of 6.9.3

# ---------- 1. PlantUML images replace the old images ----------
replace_picture(227, "q1a-1-usecase-overview")
replace_picture(246, "q1a-2-usecase-track-invoice")
replace_picture(270, "q1a-3-usecase-approve-export")
replace_picture(346, "q2b-entity-classes")
TOOL = "Visual Paradigm" if USE_VP else "PlantUML"
set_text(P(347), f"Hình 6.1 - Biểu đồ lớp thực thể của hai module ({TOOL})")
replace_picture(366, "q3a-2-analysis-classes-approve-export")
set_text(P(367), f"Hình 6.2 - Biểu đồ lớp phân tích Boundary - Entity, module 2 ({TOOL})")
replace_picture(370, "x2-state-order")
set_text(P(371), f"Hình 6.4 - Biểu đồ trạng thái của đối tượng đơn hàng ({TOOL})")
replace_picture(428, "x3-sequence-analysis-approve-export")
set_text(P(429), f"Hình 6.3 - Biểu đồ tuần tự phân tích, 51 bước ({TOOL})")

# ---------- 2. Module 2 corrections ----------
set_text(P(336), "Một SaleStaff duyệt và xuất nhiều Order; đơn chưa duyệt chưa có nhân viên, sau khi duyệt gắn đúng "
                 "một SaleStaff -> SaleStaff - Order: 0..1 - n.")
set_text(P(337), "Một DeliveryStaff được phân công nhiều Order ở các thời điểm khác nhau; đơn chỉ có nhân viên giao "
                 "hàng sau khi được phân công -> DeliveryStaff - Order: 0..1 - n.")
set_text(P(338), P(338).text.replace("Order - OrderDetail: 1 - n", "Order - OrderDetail: 1 - 1..n (mỗi đơn có "
                                     "ít nhất một dòng)"))
nouns = T(331)
for r, row in enumerate(nouns.rows):
    if row.cells[0].text == "Nhân viên giao hàng":
        set_cell(nouns, r, 2, "Lớp DeliveryStaff: deliveryStaffId, fullName, phone, area, status")
    if row.cells[0].text == "Hóa đơn":
        set_cell(nouns, r, 2, "Lớp Invoice: invoiceId, issueDate, totalAmount (trạng thái hóa đơn chính là "
                              "trạng thái của Order, không lưu riêng)")
for r, row in enumerate(nouns.rows):
    head, concl = row.cells[0].text, row.cells[2].text
    if head == "Nhân viên bán hàng":
        set_cell(nouns, r, 2, "Lớp Staff kế thừa Member: code, position; lớp SaleStaff kế thừa Staff")
    elif head == "Khách hàng":
        set_cell(nouns, r, 2, "Lớp Customer kế thừa Member: code (Member: username, password, fullName, email, "
                              "phone, address)")
    else:
        for old in ("orderId", "productId", "deliveryStaffId", "invoiceId"):
            concl = concl.replace(old, "code")
        if concl != row.cells[2].text:
            set_cell(nouns, r, 2, concl)
expect(344, "SaleStaff và DeliveryStaff")
set_text(P(344), "Customer và Staff kế thừa Member (thông tin tài khoản dùng chung); SaleStaff kế thừa Staff. "
                 "DeliveryStaff không có tài khoản trên hệ thống nên là lớp riêng. Pha phân tích chưa có thuộc tính "
                 "id: code là mã nghiệp vụ hiển thị cho người dùng (KH01, NV01, GH03, SP07, DH1024, HD1024).")
views = T(350)
for r, row in enumerate(views.rows):
    if r and row.cells[0].text != "SaleHomeView":
        set_cell(views, r, 1, row.cells[1].text + ", -subBack")
set_text(P(369), "Biểu đồ trạng thái của đối tượng Order (vòng đời đơn hàng qua hai module); hóa đơn Invoice đi "
                 "theo trạng thái của đơn. Việc \"đã phân công nhân viên giao hàng\" là điều kiện gác của export(), "
                 "không phải một trạng thái riêng, để khớp đúng sáu trạng thái trong bảng trạng thái.")
constraints = T(373)
set_cell(constraints, 1, 1, "Từ Exported không quay lại Approved - một đơn chỉ được xuất một lần")
set_cell(constraints, 2, 1, "Chuyển Approved -> Exported chỉ hợp lệ khi mọi sản phẩm đủ tồn kho")
set_cell(constraints, 3, 1, "export() chỉ thành công khi đơn đã được phân công nhân viên giao hàng (điều kiện gác)")

insert_after(anchor_state, [
    para("Biểu đồ trạng thái giao diện của module: mỗi trạng thái là một lần hệ thống hiển thị một giao diện và chờ "
         "người dùng; điều kiện chuyển trạng thái là hành động của người dùng trên giao diện đó."),
    figure("x6-state-screen-approve-export", "Hình 6.5 - Biểu đồ trạng thái giao diện module Duyệt và xuất đơn hàng"),
])
end_of_m2 = insert_after(anchor_end, [
    heading("6.9.4. Biểu đồ giao tiếp", 3),
    para("Biểu đồ giao tiếp vẽ từ kịch bản phiên bản 2: 51 thông điệp đánh số đúng như 6.9.1, chỉ dùng các lớp và "
         "quan hệ của biểu đồ lớp phân tích (Hình 6.2). Liên kết không có chiều; mũi tên nhỏ cạnh nhãn chỉ chiều "
         "thông điệp. Nhóm thông điệp: 1-7 lọc đơn chưa xuất, 8-13 xem chi tiết DH1024, 14-18 duyệt, 19-29 phân "
         "công GH03, 30-43 xuất đơn, 44-51 in hóa đơn."),
    figure("q3a-4-communication-approve-export", "Hình 6.6 - Biểu đồ giao tiếp, kịch bản chuẩn 51 bước"),
])

# ---------- 2b. Use case decomposition per screen (giáo trình 3.1.3) ----------
for i, text in [(240, "Không nên tách"), (243, "View Current Invoice Status 0"), (248, "Nghiệp vụ tổng thể"),
                (251, "Approve Order 0"), (255, "Print Invoice 0")]:
    expect(i, text)
set_text(P(240), "Theo giáo trình (mục 3.1.3), mỗi giao diện tương tác với khách hàng là một use case con; thao tác "
                 "trên cùng một giao diện (như xem trạng thái hiện tại) không tách thành use case riêng. Use case "
                 "Track Invoice 0 được phân rã thành:")
set_text(P(241), "Customer Login 0 (kế thừa Login 0) - «include»")
set_text(P(242), "View Ordered Invoice List 0 - giao diện danh sách hóa đơn, bắt buộc - «include»")
set_text(P(243), "View Invoice Detail 0 - giao diện chi tiết hóa đơn, tùy chọn từ danh sách - «extend» View Ordered "
                 "Invoice List 0")
set_text(P(244), "Trạng thái hiện tại của hóa đơn là một trường trên giao diện chi tiết, không phải use case riêng.")
set_text(P(248), "Nghiệp vụ tổng thể được mô hình hóa bằng use case Approve and Export Order 0. Trong sơ đồ chi tiết, "
                 "mỗi giao diện tương tác với nhân viên bán hàng là một use case con (giáo trình mục 3.1.3); duyệt "
                 "đơn và xác nhận xuất là hai nút trên giao diện chi tiết đơn, đóng gói là thao tác ngoài phần mềm nên "
                 "không tách thành use case. Các use case con (đều «include»):")
set_text(P(249), "Sale Staff Login 0 (kế thừa Login 0)")
set_text(P(250), "Browse Orders 0 - giao diện danh sách đơn hàng")
set_text(P(251), "View Order Detail 0 - giao diện chi tiết đơn hàng (duyệt đơn, xác nhận xuất)")
set_text(P(252), "Assign Delivery Staff 0 - giao diện chọn nhân viên giao hàng")
set_text(P(253), "Print Invoice 0 - giao diện xem trước và in hóa đơn")
for i in (254, 255):
    body[i].getparent().remove(body[i])
flow = T(260)
for r, row in enumerate(flow.rows):
    if row.cells[2].text == "Chọn Approve Order 0.":
        set_cell(flow, r, 2, "Nhấn nút Duyệt đơn trên giao diện View Order Detail 0.")
    if row.cells[2].text == "Chọn xác nhận Export Order 0.":
        set_cell(flow, r, 2, "Nhấn nút Xác nhận xuất hàng trên giao diện View Order Detail 0.")
# overview UC table lists main use cases only, as the overview diagram does
uc = T(224)
for row in list(uc.rows):
    if row.cells[1].text in ("View Invoice Detail 0", "View Order Detail 0", "Approve Order 0", "Pack Order 0",
                             "Assign Delivery Staff 0", "Export Order 0", "Print Invoice 0"):
        row._tr.getparent().remove(row._tr)
for r, row in enumerate(uc.rows):
    if row.cells[1].text == "Browse Orders 0":
        set_cell(uc, r, 1, "Approve and Export Order 0")
        set_cell(uc, r, 3, "Duyệt đơn, phân công giao hàng, xuất kho và in hóa đơn")
approve_id = None
for r, row in enumerate(uc.rows):
    if r:
        set_cell(uc, r, 0, f"UC{r:02d}")
        if row.cells[1].text == "Approve and Export Order 0":
            approve_id = f"UC{r:02d}"
spec2 = T(257)
for r, row in enumerate(spec2.rows):
    if row.cells[0].text == "Use Case ID":
        set_cell(spec2, r, 1, approve_id)

# ---------- 3. Module 1: full analysis (5.6 - 5.10) ----------
m1 = []
m1 += [heading("5.6. Kịch bản chuẩn Track Invoice 0 (có dữ liệu mẫu)", 2)]
m1 += table([
    ["Trường", "Nội dung"],
    ["Use case", "Track Invoice 0 (Theo dõi hóa đơn)"],
    ["Actor", "Customer (Khách hàng)"],
    ["Tiền điều kiện", "Khách hàng đã có tài khoản thành viên và đăng nhập thành công"],
    ["Hậu điều kiện", "Không thay đổi dữ liệu; khách hàng xem được chi tiết và trạng thái hiện tại của một hóa đơn "
                      "thuộc chính mình"],
])
m1 += [para(bold_prefix="Kịch bản chính:"),
       para("1. Khách hàng Nguyễn Văn An (KH01) chọn menu \"Theo dõi hóa đơn\" trên giao diện chính của khách hàng "
            "(06/09/2026 10:00)."),
       para("2. Hệ thống hiển thị danh sách hóa đơn của các đơn khách đã đặt, mới nhất trước:")]
m1 += table([
    ["Mã HĐ", "Mã đơn", "Ngày đặt", "Số mặt hàng", "Tổng tiền", "Trạng thái"],
    ["HD1024", "DH1024", "05/09/2026", "3", "1.250.000", "Đã xuất"],
    ["HD1011", "DH1011", "01/09/2026", "1", "175.000", "Đã hủy"],
    ["HD0987", "DH0987", "20/08/2026", "1", "540.000", "Đã giao"],
])
m1 += [para("3. Khách hàng click dòng số 1 (mã hóa đơn = HD1024)."),
       para("4. Hệ thống kiểm tra hóa đơn HD1024 thuộc khách hàng đang đăng nhập và hiển thị giao diện chi tiết hóa "
            "đơn: mã hóa đơn HD1024, mã đơn DH1024, ngày đặt 05/09/2026, ngày lập hóa đơn 06/09/2026, địa chỉ nhận "
            "25 Trần Duy Hưng, Cầu Giấy, Hà Nội, danh sách sản phẩm:")]
m1 += table([
    ["Mã SP", "Tên sản phẩm", "Số lượng", "Đơn giá", "Thành tiền"],
    ["SP07", "Gạo ST25 5kg", "2", "250.000", "500.000"],
    ["SP15", "Dầu ăn Neptune 1L", "5", "60.000", "300.000"],
    ["SP22", "Sữa tươi Vinamilk 1L", "10", "45.000", "450.000"],
    ["", "Tổng tiền", "", "", "1.250.000"],
])
m1 += [para("Trạng thái hiện tại: \"Đã xuất\" (xuất lúc 06/09/2026 09:15, nhân viên giao hàng Phạm Văn Dũng - "
            "0912345678), kèm nút \"Quay lại\"."),
       para("5. Khách hàng xem thông tin và click \"Quay lại\"."),
       para("6. Hệ thống hiển thị lại danh sách hóa đơn ở bước 2."),
       para(bold_prefix="Ngoại lệ của kịch bản chuẩn:"),
       para("2a. Khách hàng chưa có đơn hàng nào."),
       para("2a.1 Hệ thống hiển thị thông báo \"Bạn chưa có hóa đơn nào\"."),
       para("2a.2 Khách hàng nhấn OK và quay về giao diện chính của khách hàng."),
       para("4a. Mã hóa đơn yêu cầu không thuộc khách hàng hiện tại (ví dụ sửa invoiceId=HD1025 trên URL)."),
       para("4a.1 Hệ thống kiểm tra quyền sở hữu ở phía server, hiển thị \"Không tìm thấy hóa đơn\" và không hiển thị "
            "dữ liệu nào của hóa đơn đó (BR01)."),
       para("4a.2 Khách hàng quay về danh sách hóa đơn (Bước 2)."),
       para("4b. Khách hàng chọn hóa đơn của đơn đã hủy (HD1011)."),
       para("4b.1 Hệ thống vẫn hiển thị thông tin lịch sử với trạng thái \"Đã hủy\" và ngày lập \"Chưa lập\"."),
       para("Ghi chú: mỗi đơn có một hóa đơn ngay từ lúc đặt (Order 1 - 1 Invoice) để khách theo dõi được; ngày lập "
            "hóa đơn chỉ được ghi khi nhân viên bán hàng xuất đơn (bước 18 của module 2). Kịch bản này diễn ra sau "
            "kịch bản 6.5 nên HD1024 đang ở trạng thái Đã xuất.", italic=True)]

m1 += [heading("5.7. Mô hình hóa lớp - trích lớp thực thể của module", 2),
       heading("5.7.1. Bước 1 - Mô tả chức năng bằng văn xuôi", 3),
       para("Khách hàng đăng nhập vào hệ thống rồi chọn chức năng theo dõi hóa đơn. Hệ thống hiển thị danh sách hóa "
            "đơn của các đơn hàng khách đã đặt, mỗi hóa đơn gồm mã hóa đơn, mã đơn, ngày đặt, số mặt hàng, tổng tiền "
            "và trạng thái hiện tại của đơn. Khách hàng chọn một hóa đơn; hệ thống kiểm tra hóa đơn thuộc khách hàng "
            "rồi hiển thị chi tiết: ngày lập hóa đơn, địa chỉ nhận hàng, các dòng sản phẩm với số lượng, đơn giá, "
            "thành tiền, tổng tiền, trạng thái hiện tại, thời điểm xuất và nhân viên giao hàng phụ trách."),
       heading("5.7.2. Bước 2 + 3 - Trích danh từ và đánh giá", 3)]
m1 += table([
    ["Danh từ", "Đánh giá", "Kết luận"],
    ["Hệ thống, menu, giao diện, danh sách", "Quá chung hoặc thuộc tầng giao diện", "Loại"],
    ["Khách hàng", "Chủ sở hữu hóa đơn, người đặt đơn", "Lớp Customer kế thừa Member: code (Member: username, password, fullName, email, phone, address)"],
    ["Hóa đơn, mã hóa đơn, ngày lập", "Chứng từ khách theo dõi", "Lớp Invoice: code, issueDate, totalAmount"],
    ["Đơn hàng, ngày đặt, địa chỉ nhận", "Hóa đơn gắn với đúng một đơn", "Lớp Order (như 6.6.2)"],
    ["Dòng sản phẩm, số lượng, đơn giá, thành tiền", "Mỗi dòng gắn một sản phẩm", "Lớp OrderDetail: quantity, "
                                                     "unitPrice, lineAmount"],
    ["Sản phẩm", "Hàng hóa trong đơn", "Lớp Product (như 6.6.2)"],
    ["Trạng thái hiện tại", "Hóa đơn đi theo trạng thái của đơn", "Thuộc tính status của Order"],
    ["Nhân viên giao hàng", "Khách xem được người giao", "Lớp DeliveryStaff: code, fullName, phone, area, status"],
    ["Quyền sở hữu hóa đơn", "Ràng buộc nghiệp vụ BR01 qua Customer - Order - Invoice", "Loại (không phải lớp)"],
])
m1 += [para("Kết quả: module 1 dùng 6 trong 7 lớp thực thể của module 2 (Customer, Order, OrderDetail, Product, "
            "Invoice, DeliveryStaff; không cần SaleStaff). Quan hệ số lượng và quan hệ bổ sung như 6.6.3 - 6.6.4; "
            "biểu đồ lớp thực thể chung cho hai module ở Hình 6.1. Pha phân tích chưa có thuộc tính id; code là mã "
            "nghiệp vụ hiển thị cho người dùng (KH01, DH1024, HD1024...), id được bổ sung ở pha thiết kế (chương 7).")]

m1 += [heading("5.8. Biểu đồ lớp phân tích (Boundary - Entity)", 2),
       heading("5.8.1. Lớp Boundary và thành phần giao diện", 3)]
m1 += table([
    ["Lớp Boundary", "Thành phần"],
    ["CustomerHomeView", "-subTrackInvoice"],
    ["InvoiceListView", "-outsubInvoiceList, -subBack"],
    ["InvoiceDetailView", "-outInvoiceInfo, -outsubItemList, -outTotalAmount, -outStatus, -subBack"],
])
m1 += [heading("5.8.2. Phương thức và lý do gán vào lớp thực thể", 3)]
m1 += table([
    ["Phương thức", "Entity", "Lý do"],
    ["getInvoiceByCustomer()", "Invoice", "Đầu ra là danh sách Invoice của khách hàng đang đăng nhập"],
    ["getInvoiceDetail()", "Invoice", "Đầu ra là một Invoice kèm các dòng hàng và trạng thái của đơn; dùng lại ở "
                                      "module 2 để in hóa đơn"],
])
m1 += [heading("5.8.3. Diễn giải chi tiết", 3),
       bullet("Sau khi đăng nhập, hệ thống hiển thị giao diện chính của khách hàng -> đề xuất lớp CustomerHomeView, "
              "có nút -subTrackInvoice để vào chức năng theo dõi hóa đơn."),
       bullet("Khách hàng click -subTrackInvoice -> giao diện danh sách hóa đơn hiện lên -> đề xuất lớp "
              "InvoiceListView, có -outsubInvoiceList để hiển thị và chọn hóa đơn, -subBack để quay lại. Để có danh "
              "sách cần chức năng getInvoiceByCustomer() của Invoice (input: khách hàng; output: danh sách Invoice)."),
       bullet("Khách hàng click một hóa đơn -> giao diện chi tiết hiện lên -> đề xuất lớp InvoiceDetailView, có "
              "-outInvoiceInfo, -outsubItemList, -outTotalAmount, -outStatus và -subBack. Dữ liệu lấy qua "
              "getInvoiceDetail() của Invoice (input: hóa đơn, khách hàng; output: Invoice)."),
       bullet("Quan hệ giữa các lớp thực thể giữ nguyên như biểu đồ lớp thực thể (Hình 6.1).")]
m1 += [heading("5.8.4. Biểu đồ lớp phân tích", 3),
       figure("q3a-1-analysis-classes-track-invoice", "Hình 5.1 - Biểu đồ lớp phân tích Boundary - Entity, module 1")]

m1 += [heading("5.9. Biểu đồ trạng thái", 2),
       para("Mỗi trạng thái là một lần hệ thống hiển thị một giao diện và chờ khách hàng; điều kiện chuyển trạng thái "
            "là hành động của khách hàng trên giao diện đó."),
       figure("x5-state-screen-track-invoice", "Hình 5.2 - Biểu đồ trạng thái giao diện module Theo dõi hóa đơn")]

v2 = [
    "Khách hàng click nút subTrackInvoice trên giao diện CustomerHomeView.",
    "Lớp CustomerHomeView gọi lớp InvoiceListView.",
    "Lớp InvoiceListView gọi lớp Invoice yêu cầu tìm các hóa đơn của khách hàng.",
    "Lớp Invoice gọi phương thức getInvoiceByCustomer().",
    "Lớp Invoice trả danh sách hóa đơn (HD1024, HD1011, HD0987) về cho InvoiceListView.",
    "Lớp InvoiceListView hiển thị danh sách hóa đơn cho khách hàng.",
    "Khách hàng click hóa đơn HD1024 trong outsubInvoiceList.",
    "Lớp InvoiceListView gọi lớp InvoiceDetailView.",
    "Lớp InvoiceDetailView gọi lớp Invoice yêu cầu lấy chi tiết hóa đơn HD1024.",
    "Lớp Invoice gọi phương thức getInvoiceDetail().",
    "Lớp Invoice trả thông tin hóa đơn, các dòng hàng và trạng thái hiện tại của đơn về cho InvoiceDetailView.",
    "Lớp InvoiceDetailView hiển thị chi tiết hóa đơn và trạng thái \"Đã xuất\" cho khách hàng.",
    "Khách hàng click nút subBack.",
    "Lớp InvoiceDetailView gọi lại lớp InvoiceListView.",
    "Lớp InvoiceListView hiển thị lại danh sách hóa đơn cho khách hàng.",
]
m1 += [heading("5.10. Kịch bản chi tiết phiên bản 2.0 (Actor - Boundary - Entity)", 2),
       heading("5.10.1. Kịch bản phiên bản 2 - 15 bước", 3)]
m1 += [para(f"{n}. {text}") for n, text in enumerate(v2, 1)]
m1 += [heading("5.10.2. Biểu đồ giao tiếp", 3),
       para("Vẽ từ kịch bản phiên bản 2, số thứ tự thông điệp khớp đúng 15 bước ở 5.10.1; chỉ dùng các lớp và quan hệ "
            "của biểu đồ lớp phân tích (Hình 5.1)."),
       figure("q3a-3-communication-track-invoice", "Hình 5.3 - Biểu đồ giao tiếp, kịch bản chuẩn 15 bước"),
       heading("5.10.3. Biểu đồ tuần tự phân tích", 3),
       figure("x4-sequence-analysis-track-invoice", "Hình 5.4 - Biểu đồ tuần tự phân tích, 15 bước"),
       heading("5.10.4. Ngoại lệ của kịch bản phiên bản 2", 3),
       para(bold_prefix="Ngoại lệ 1: getInvoiceByCustomer() không tìm thấy hóa đơn nào"),
       para("Lớp Invoice trả về danh sách rỗng cho InvoiceListView."),
       para("Lớp InvoiceListView hiển thị thông báo \"Bạn chưa có hóa đơn nào\"; khách hàng quay về CustomerHomeView."),
       para(bold_prefix="Ngoại lệ 2: hóa đơn không thuộc khách hàng đang đăng nhập"),
       para("Lớp Invoice không trả dữ liệu cho InvoiceDetailView."),
       para("Lớp InvoiceDetailView hiển thị \"Không tìm thấy hóa đơn\"; khách hàng quay về danh sách (bước 6)."),
       para(bold_prefix="Ngoại lệ 3: hóa đơn của đơn đã hủy"),
       para("Lớp InvoiceDetailView vẫn hiển thị thông tin lịch sử, trạng thái \"Đã hủy\" và ngày lập \"Chưa lập\".")]
insert_after(anchor_m1, m1)

# ---------- 4. First page: the exam question ----------
from docx.enum.text import WD_BREAK  # noqa: E402

question = []
question.append(heading("ĐỀ BÀI", 1))
for raw in (ROOT / "question.md").read_text(encoding="utf-8").splitlines():
    line = raw.replace("**", "").strip()
    if not line:
        continue
    if line.startswith("* "):
        question.append(bullet(line[2:]))
    elif line.startswith("Question"):
        question.append(para(bold_prefix=line))
    else:
        question.append(para(line))
brk = d.add_paragraph()
brk.add_run().add_break(WD_BREAK.PAGE)
question.append(brk._p)
for el in question:
    first_element.addprevious(el)

# ---------- 5. Chapter 7: design (textbook chapter 4) ----------
def numbered(lines):
    return [para(f"{n}. {text}") for n, text in enumerate(lines, 1)]


ch7 = [heading("7. Thiết kế", 1),
       para("Thiết kế theo giáo trình BG HP TTTN 2 CNPM 2020 (chương 4), nền tảng J2EE: tầng giao diện là các trang "
            "gd*.jsp (hiển thị) và do*.jsp (xử lí submit); tầng truy cập dữ liệu là lớp cơ sở DAO giữ kết nối tĩnh "
            "dùng chung và các lớp XxxDAO kế thừa DAO; tầng thực thể là các lớp của biểu đồ thực thể pha thiết kế."),
       heading("7.1. Thiết kế lớp thực thể của hệ thống", 2),
       bullet("Bước 1: bổ sung id : int cho mọi lớp không kế thừa lớp khác (Member, DeliveryStaff, Supplier, "
              "ProductCategory, Product, ImportReceipt, ImportReceiptDetail, Order, OrderDetail, Invoice)."),
       bullet("Bước 2: bổ sung kiểu dữ liệu Java (int, double, String, Date)."),
       bullet("Bước 3: chuyển association thành composition (Order - OrderDetail, ImportReceipt - "
              "ImportReceiptDetail) và aggregation (các quan hệ tham chiếu còn lại)."),
       bullet("Bước 4: lớp chứa khai báo thuộc tính đối tượng, dùng [] cho quan hệ nhiều (details : OrderDetail[]). "
              "Các lớp thống kê CustomerStat, SupplierStat, ImportStat, ExportStat kế thừa lớp thực thể tương ứng."),
       figure("q2c-design-entity-classes-system", "Hình 7.1 - Biểu đồ lớp thực thể pha thiết kế của hệ thống"),
       heading("7.2. Thiết kế CSDL của hệ thống", 2)]
ch7 += table([
    ["Bước", "Áp dụng"],
    ["1 - 2", "Mỗi lớp thực thể -> một bảng tbl...; chỉ lấy thuộc tính kiểu cơ bản, chuyển sang kiểu SQL "
              "(integer(10), varchar(255), float(10), date, datetime)."],
    ["3", "Quan hệ 1-n giữ nguyên. Order 1-1 Invoice -> gộp hóa đơn vào tblOrder (invoiceCode, issueDate)."],
    ["4", "Khóa chính id; bảng lớp con tblCustomer, tblStaff dùng tblMemberid vừa là khóa chính vừa là khóa "
          "ngoại; khóa ngoại đặt tên tbl<Bảng>id."],
    ["5", "Loại thuộc tính dẫn xuất totalAmount, lineAmount (tính từ số lượng x đơn giá). Loại bảng "
          "tblSaleStaff, tblManagementStaff (chỉ còn một khóa ngoại, phân biệt bằng tblMember.role) và các bảng "
          "thống kê. Giữ tblOrderDetail.unitPrice vì là giá tại thời điểm đặt (BR08)."],
])
ch7 += [para("Kết quả có 11 bảng, mọi khóa ngoại đều có chỉ mục; script sql/system_schema.sql chạy được trên MySQL 8 "
             "và đã kiểm tra trên SQLite với khóa ngoại được bật."),
        figure("q4a-database-system", "Hình 7.2 - Biểu đồ CSDL của hệ thống"),
        para(bold_prefix="CSDL liên quan đến hai module. "),
        para("Ánh xạ các lớp thực thể của hai module (phân tích, mục 6.6) sang bảng:")]
ch7 += table([
    ["Lớp thực thể", "Bảng", "Ghi chú"],
    ["Member", "tblMember", "Lớp cha: tài khoản, họ tên, điện thoại, địa chỉ, role"],
    ["Customer", "tblCustomer", "tblMemberid vừa là khóa chính vừa là khóa ngoại"],
    ["Staff, SaleStaff", "tblStaff", "SaleStaff không có thuộc tính riêng nên không có bảng riêng; phân biệt bằng role"],
    ["DeliveryStaff", "tblDeliveryStaff", "activeOrderCount là thuộc tính dẫn xuất, không lưu"],
    ["Product", "tblProduct", "Khóa ngoại tới tblProductCategory"],
    ["Order", "tblOrder", "totalAmount dẫn xuất, không lưu"],
    ["OrderDetail", "tblOrderDetail", "lineAmount dẫn xuất, không lưu; giữ unitPrice (BR08)"],
    ["Invoice", "gộp vào tblOrder", "Quan hệ 1-1 nên gộp: invoiceCode, issueDate"],
])
ch7 += [figure("q4a-2-database-two-modules", "Hình 7.2.1 - CSDL liên quan đến hai module (8 bảng, tập con của CSDL hệ thống)")]

MODULE_DESIGN = [
    ("7.3", "Module 1 - Customer tracks invoice", "track-invoice", "Track Invoice 0", [
        ("q3b-1-ui-m1-1-customer-home", "Giao diện chính khách hàng (gdCustomerHome.jsp)"),
        ("q3b-1-ui-m1-2-invoice-list", "Danh sách hóa đơn (gdInvoiceList.jsp)"),
        ("q3b-1-ui-m1-3-invoice-detail", "Chi tiết hóa đơn (gdInvoiceDetail.jsp)"),
    ], "q3b-3-design-classes-track-invoice",
     "Trang gdInvoiceList.jsp và gdInvoiceDetail.jsp dùng InvoiceDAO. Hàm getInvoiceDetail(idInvoice, idCustomer) "
     "chỉ trả về hóa đơn thuộc khách hàng đang đăng nhập (BR01).",
     "q3c-1-activity-track-invoice", "q3c-3-sequence-design-track-invoice", []),
    ("7.4", "Module 2 - Sale staff approves orders + export", "approve-export", "Approve and Export Order 0", [
        ("q3b-2-ui-m2-1-sale-home", "Giao diện chính nhân viên bán hàng (gdSaleHome.jsp)"),
        ("q3b-2-ui-m2-2-order-list", "Danh sách đơn hàng (gdOrderList.jsp)"),
        ("q3b-2-ui-m2-3-order-detail", "Chi tiết đơn hàng (gdOrderDetail.jsp)"),
        ("q3b-2-ui-m2-4-delivery-staff-list", "Chọn nhân viên giao hàng (gdDeliveryStaffList.jsp)"),
        ("q3b-2-ui-m2-5-invoice-print", "Xem trước và in hóa đơn (gdInvoicePrint.jsp)"),
    ], "q3b-4-design-classes-approve-export",
     "Ba trang doApproveOrder.jsp, doSaveAssign.jsp, doExportOrder.jsp set thuộc tính cho đối tượng Order rồi gọi "
     "OrderDAO lưu. OrderDAO.exportOrder() dùng ProductDAO và InvoiceDAO trên cùng kết nối tĩnh của DAO nên trừ "
     "tồn kho, đổi trạng thái và lập hóa đơn nằm trong một giao dịch (BR05).",
     "q3c-2-activity-approve-export", "q3c-4-sequence-design-approve-export",
     ["Ngoại lệ: exportOrder() rollback toàn bộ giao dịch và doExportOrder.jsp thông báo lỗi khi checkStock() báo "
      "thiếu hàng (16b), đơn đã được xuất trước đó (16a) hoặc chưa được phân công nhân viên giao hàng (16c); "
      "doApproveOrder.jsp thông báo lỗi khi đơn đã bị hủy (8)."]),
]
for num, title, module, uc, screens, classes, class_note, activity, sequence, notes in MODULE_DESIGN:
    fig = iter(range(1, 50))
    ch7 += [heading(f"{num}. {title}", 2),
            heading(f"{num}.1. Thiết kế giao diện", 3),
            para("Mỗi giao diện ứng với một lớp biên pha phân tích; các cột khớp bảng dữ liệu của kịch bản chuẩn, "
                 "mọi màn hình con có nút Quay lại.")]
    for name, caption in screens:
        ch7 += figure(name, f"Hình {num}.{next(fig)} - {caption}")
    steps = generate.scenario_v3(module)
    ch7 += [heading(f"{num}.2. Sơ đồ lớp thiết kế", 3), para(class_note),
            figure(classes, f"Hình {num}.{next(fig)} - Biểu đồ lớp thiết kế module {uc}"),
            heading(f"{num}.3. Biểu đồ hoạt động", 3),
            para("Mỗi vùng là phần xử lí tại một trang JSP; mỗi hoạt động ứng với một phương thức đã thiết kế, lời "
                 "gọi DAO vẽ bằng nút đối tượng."),
            figure(activity, f"Hình {num}.{next(fig)} - Biểu đồ hoạt động module {uc}"),
            heading(f"{num}.4. Kịch bản phiên bản 3 - {len(steps)} bước", 3),
            para("Tên hành động là tên phương thức đã thiết kế; các bước đóng gói thuộc tính con của lớp thực thể "
                 "được lược bỏ cho gọn.", italic=True),
            *numbered(steps), *[para(n) for n in notes],
            heading(f"{num}.5. Biểu đồ tuần tự thiết kế", 3),
            figure(sequence, f"Hình {num}.{next(fig)} - Biểu đồ tuần tự thiết kế, {len(steps)} bước")]
ch7 += [heading("7.5. Biểu đồ gói", 2),
        para("Theo giáo trình mục 4.3.3: lớp thực thể trong gói model, lớp DAO trong gói dao, trang JSP trong gói view; "
             "gói view chia theo người dùng: thanhvien (gdLogin.jsp, doLogin.jsp), khachhang (3 trang của module 1), "
             "nhanvienbanhang (5 trang gd*.jsp và 3 trang do*.jsp của module 2). Mọi lớp trong hình đều có mã nguồn "
             "ở chương 8."),
        figure("q5a-package", "Hình 7.5 - Biểu đồ gói"),
        heading("7.6. Biểu đồ triển khai (MVC trên J2EE)", 2),
        bullet("Máy khách: trình duyệt nhận trang HTML do JSP sinh ra qua HTTP/HTTPS; in hóa đơn bằng lệnh in của "
               "trình duyệt."),
        bullet("Web Server: Apache Tomcat 10+ (Jakarta EE) chạy deptstore.war. View là các trang gd*.jsp; Controller "
               "là các trang do*.jsp và gói dao (giáo trình gọi lớp DAO là lớp điều khiển); Model là gói model. Lớp "
               "dao, model nằm trong WEB-INF/classes, JDBC driver trong WEB-INF/lib."),
        bullet("Database Server: MySQL 8 chứa CSDL 11 bảng (mục 7.2), kết nối qua JDBC (TCP 3306)."),
        figure("q5b-deployment", "Hình 7.6 - Biểu đồ triển khai")]
end_of_ch7 = insert_after(end_of_m2, ch7)

# ---------- 6. Chapter 8: implementation (question 4b) ----------
def code_block(text):
    out = []
    for line in text.rstrip("\n").splitlines():
        p = d.add_paragraph(style="normal")
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line if line.strip() else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(8)
        out.append(p._p)
    out.append(para())
    return out


def method_body(path, signature):
    src = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(src) if signature in l)
    while start > 0 and src[start - 1].strip().startswith(("/**", "*", "*/")):
        start -= 1
    depth, end = 0, start
    for end in range(start, len(src)):
        depth += src[end].count("{") - src[end].count("}")
        if "{" in "".join(src[start:end + 1]) and depth == 0:
            break
    return "\n".join(src[start:end + 1])


JAVA = ROOT / "java"
ch8 = [heading("8. Cài đặt (câu 4b)", 1),
       para("Mã nguồn cài đặt đúng thiết kế chương 7 và CSDL mục 7.2, tổ chức như giáo trình mục 5.1: java/src/model "
            "(lớp thực thể), java/src/dao (lớp DAO), java/WebContent (trang JSP), java/test (kiểm thử). Mặc định kết "
            "nối MySQL; đã chạy kiểm thử 25/25 ca (22 ca đơn vị cho DAO, 3 ca chạy toàn bộ trang JSP trong Tomcat)."),
       heading("8.1. Khung lớp", 2)]
ch8 += table([
    ["Gói", "Lớp", "Vai trò"],
    ["model", "Member, Customer, Staff, SaleStaff, DeliveryStaff, Product, Order, OrderDetail, Invoice",
     "JavaBean: thuộc tính private và getter/setter; Order có thêm getStatusLabel() cho giao diện"],
    ["dao", "DAO", "Giữ kết nối tĩnh con dùng chung; lớp con gọi super()"],
    ["dao", "MemberDAO, InvoiceDAO, OrderDAO, OrderDetailDAO, ProductDAO, DeliveryStaffDAO",
     "Kế thừa DAO; mỗi phương thức ứng với một phương thức trong biểu đồ lớp thiết kế"],
    ["view", "gdLogin.jsp, doLogin.jsp, khachhang/*.jsp, nhanvienbanhang/*.jsp",
     "Kiểm tra phiên đăng nhập, gọi DAO, lưu đối tượng vào session, hiển thị; do*.jsp set thuộc tính rồi lưu"],
])
ch8 += [para(bold_prefix="Lớp DAO cơ sở:"),
        *code_block((JAVA / "src" / "dao" / "DAO.java").read_text(encoding="utf-8")),
        para(bold_prefix="Phương thức xuất đơn trong một giao dịch (OrderDAO.exportOrder):"),
        *code_block(method_body(JAVA / "src" / "dao" / "OrderDAO.java", "public boolean exportOrder(Order order)")),
        heading("8.2. Giải thích các phương thức", 2)]
ch8 += table([
    ["Lớp", "Phương thức", "Hoạt động"],
    ["MemberDAO", "checkLogin(username, password)",
     "Tìm thành viên đang hoạt động, trả về Customer / SaleStaff theo role, sai thì null"],
    ["InvoiceDAO", "getInvoiceByCustomer(idCustomer)",
     "Hóa đơn (gộp trong tblOrder) của khách, mới nhất trước; tổng tiền = SUM(quantity x unitPrice)"],
    ["InvoiceDAO", "getInvoiceDetail(idInvoice, idCustomer)",
     "Điều kiện o.id = ? AND o.tblCustomerid = ? nên hóa đơn của khách khác trả null (BR01)"],
    ["InvoiceDAO", "issueInvoice(order)", "Ghi issueDate khi xuất; chỉ lập một lần; chạy trong giao dịch xuất đơn"],
    ["OrderDAO", "getUnexportedOrder()", "Đơn PENDING / APPROVED kèm khách hàng, tổng tiền, dòng hàng"],
    ["OrderDAO", "approveOrder(order)", "Ghi trạng thái, nhân viên, thời điểm duyệt; chỉ khi đơn còn PENDING (ngoại lệ 8)"],
    ["OrderDAO", "assignDeliveryStaff(order)", "Gán khi đơn APPROVED và nhân viên giao hàng không INACTIVE"],
    ["OrderDAO", "exportOrder(order)",
     "Một giao dịch: kiểm tra tồn kho, đổi APPROVED sang EXPORTED, trừ tồn kho, lập hóa đơn; lỗi thì rollback"],
    ["OrderDetailDAO", "getOrderDetailByOrder(idOrder)", "Dòng hàng kèm sản phẩm và tồn kho; lineAmount tính khi đọc"],
    ["ProductDAO", "checkStock(listDetail)", "So tồn kho hiện tại với số lượng đặt, ghi tồn kho vào từng Product"],
    ["ProductDAO", "decreaseStock(listDetail)", "Trừ tồn kho với điều kiện stockQuantity >= số lượng: không trừ âm"],
    ["DeliveryStaffDAO", "getAvailableDeliveryStaff()", "Nhân viên không INACTIVE, người sẵn sàng trước, kèm số đơn đang giao"],
])
ch8 += [heading("8.3. Kiểm thử đơn vị", 2),
        para("Theo giáo trình mục 5.3: JUnit, mỗi ca chạy trên CSDL mới dựng từ script (tương đương rollback sau mỗi ca).")]
ch8 += table([
    ["TT", "Chức năng", "Lớp điều khiển", "Phương thức", "Trường hợp test"],
    ["1", "Theo dõi hóa đơn", "InvoiceDAO", "getInvoiceByCustomer()", "KH có 3 hóa đơn; KH chưa có hóa đơn"],
    ["", "", "", "getInvoiceDetail()", "Hóa đơn của chính KH; của KH khác (BR01); không tồn tại"],
    ["", "", "", "issueInvoice()", "Lập lần đầu; lập lần hai bị từ chối"],
    ["2", "Duyệt và xuất đơn", "OrderDAO", "getUnexportedOrder()", "3 đơn chưa xuất, đúng khách, số mặt hàng, tổng tiền"],
    ["", "", "", "approveOrder()", "Đơn chờ duyệt; đơn đã hủy (ngoại lệ 8)"],
    ["", "", "", "assignDeliveryStaff()", "Đơn chưa duyệt; nhân viên nghỉ việc; hợp lệ"],
    ["", "", "", "exportOrder()", "Kịch bản chuẩn; xuất lần hai (16a); chưa phân công (16c); thiếu hàng (16b)"],
    ["", "", "OrderDetailDAO", "getOrderDetailByOrder()", "Đơn 3 dòng; đơn không tồn tại"],
    ["", "", "ProductDAO", "checkStock(), decreaseStock()", "Đủ hàng; thiếu hàng; trừ đủ; từ chối trừ âm"],
    ["", "", "DeliveryStaffDAO", "getAvailableDeliveryStaff()", "GH03 (1), GH05 (0), GH08 (3), không có GH09"],
    ["3", "Đăng nhập", "MemberDAO", "checkLogin()", "Khách hàng; nhân viên bán hàng; sai mật khẩu"],
])
insert_after(end_of_ch7, ch8)

OUT.parent.mkdir(exist_ok=True)
d.save(OUT)
print(f"wrote {OUT.relative_to(ROOT)}")
if USE_VP:
    raise SystemExit

# ---------- 7. Design-phase submission: exam question + chapter 7 only ----------
DESIGN_OUT = ROOT / "submission_ready" / "Thiet_ke_3" / "34_B23DCAT280_v5_2026-10-26_ThietKe3.docx"
DESIGN_OUT.parent.mkdir(parents=True, exist_ok=True)
design = docx.Document(OUT)
els = list(design.element.body.iterchildren())
texts = [Paragraph(e, design).text if e.tag.endswith("}p") else None for e in els]
first_report = next(i for i, e in enumerate(els) if e.tag.endswith("}p") and e.xpath(".//w:br[@w:type='page']")) + 1
ch7_start = texts.index("7. Thiết kế")
ch8_start = texts.index("8. Cài đặt (câu 4b)")
for e in els[first_report:ch7_start] + [e for e in els[ch8_start:] if not e.tag.endswith("}sectPr")]:
    e.getparent().remove(e)
design.save(DESIGN_OUT)
print(f"wrote {DESIGN_OUT.relative_to(ROOT)}")
