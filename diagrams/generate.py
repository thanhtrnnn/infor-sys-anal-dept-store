#!/usr/bin/env python3
"""Generate the PlantUML sources that are derived from other sources, so they can never drift apart.

1. Scenario v3 (design, giáo trình mục 4.3.2) for both modules is the single source of truth below (V3_*):
   - q3c-3 / q3c-4: design sequence diagrams, one arrow per numbered step;
   - scenario_v3(module) returns the numbered Vietnamese text (used by build_docx.py and answer.md).
2. q3a-3 / q3a-4: analysis communication diagrams generated from the analysis sequences x4 / x3 (scenario v2).
3. q4a-database-system / q4a-2-database-two-modules: DB diagrams generated from sql/system_schema.sql.

Run: python3 diagrams/generate.py   (then python3 export_diagrams.py)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "diagrams" / "src"

# ---------------------------------------------------------------------------------------------
# 1. Scenario v3. Each step: (from, to, arrow label, Vietnamese sentence). "A" = actor.
#    Arrows whose label starts with "trả về", "hiển thị", "thông báo" or "in hóa đơn" are returns (dashed).
# ---------------------------------------------------------------------------------------------
M1_PARTICIPANTS = [
    ("actor", "A", "Khách hàng"),
    ("boundary", "gdCustomerHome", "gdCustomerHome.jsp"),
    ("boundary", "gdInvoiceList", "gdInvoiceList.jsp"),
    ("boundary", "gdInvoiceDetail", "gdInvoiceDetail.jsp"),
    ("control", "InvoiceDAO", "InvoiceDAO"),
    ("entity", "Invoice", "Invoice"),
]


def fetch(page, dao, method, entity, what):
    """The book's 7-step 'lấy dữ liệu' pattern: JSP -> DAO -> method -> Entity packs -> back -> display."""
    return [
        (page, dao, "gọi", f"Trang {page}.jsp gọi lớp {dao} yêu cầu {what}."),
        (dao, dao, method, f"Lớp {dao} gọi hàm {method}."),
        (dao, entity, "gọi", f"Hàm {method.split('(')[0]}() gọi lớp {entity} để đóng gói thông tin."),
        (entity, entity, f"{entity}()", f"Lớp {entity} đóng gói thông tin thực thể."),
        (entity, dao, "trả về", f"Lớp {entity} trả kết quả cho hàm {method.split('(')[0]}()."),
        (dao, page, "trả về", f"Hàm {method.split('(')[0]}() trả kết quả cho trang {page}.jsp."),
    ]


def save(page, entity, setters, dao, method, what, back, actor, done):
    """The book's 'lưu' pattern: do*.jsp sets entity attributes, calls DAO, notifies, returns to a page."""
    return [
        (page, entity, "gọi", f"Trang {page}.jsp gọi lớp {entity} yêu cầu set {what}."),
        (entity, entity, setters, f"Lớp {entity} gọi các hàm {setters}."),
        (entity, page, "trả về", f"Lớp {entity} trả đối tượng về cho trang {page}.jsp."),
        (page, dao, "gọi", f"Trang {page}.jsp gọi lớp {dao} yêu cầu lưu."),
        (dao, dao, method, f"Lớp {dao} gọi hàm {method}."),
        (dao, page, "trả về", f"Lớp {dao} trả kết quả cho trang {page}.jsp."),
        (page, "A", "thông báo thành công", f"Trang {page}.jsp thông báo \"{done}\"."),
        ("A", page, "click OK", f"{actor} click OK của thông báo."),
        (page, back, "gọi", f"Trang {page}.jsp gọi lại trang {back}.jsp."),
    ]


V3_M1 = [
    ("A", "gdCustomerHome", "click Theo dõi hóa đơn",
     "Tại trang gdCustomerHome.jsp, sau khi đăng nhập, khách hàng click chọn chức năng theo dõi hóa đơn."),
    ("gdCustomerHome", "gdInvoiceList", "gọi", "Trang gdCustomerHome.jsp gọi trang gdInvoiceList.jsp."),
    *fetch("gdInvoiceList", "InvoiceDAO", "getInvoiceByCustomer(idCustomer)", "Invoice",
           "lấy danh sách hóa đơn của khách hàng"),
    ("gdInvoiceList", "A", "hiển thị", "Trang gdInvoiceList.jsp hiển thị danh sách hóa đơn cho khách hàng."),
    ("A", "gdInvoiceList", "click HD1024", "Khách hàng click hóa đơn HD1024."),
    ("gdInvoiceList", "gdInvoiceDetail", "gọi", "Trang gdInvoiceList.jsp gọi trang gdInvoiceDetail.jsp."),
    *fetch("gdInvoiceDetail", "InvoiceDAO", "getInvoiceDetail(idInvoice, idCustomer)", "Invoice",
           "lấy chi tiết hóa đơn HD1024 của khách hàng"),
    ("gdInvoiceDetail", "A", "hiển thị",
     "Trang gdInvoiceDetail.jsp hiển thị chi tiết hóa đơn và trạng thái hiện tại cho khách hàng."),
    ("A", "gdInvoiceDetail", "click Quay lại", "Khách hàng click nút Quay lại."),
    ("gdInvoiceDetail", "gdInvoiceList", "gọi", "Trang gdInvoiceDetail.jsp gọi lại trang gdInvoiceList.jsp."),
    ("gdInvoiceList", "A", "hiển thị", "Trang gdInvoiceList.jsp hiển thị lại danh sách hóa đơn."),
]

M2_PARTICIPANTS = [
    ("actor", "A", "NV bán hàng"),
    ("boundary", "gdSaleHome", "gdSaleHome.jsp"),
    ("boundary", "gdOrderList", "gdOrderList.jsp"),
    ("boundary", "gdOrderDetail", "gdOrderDetail.jsp"),
    ("boundary", "doApproveOrder", "doApproveOrder.jsp"),
    ("boundary", "gdDeliveryStaffList", "gdDeliveryStaffList.jsp"),
    ("boundary", "doSaveAssign", "doSaveAssign.jsp"),
    ("boundary", "doExportOrder", "doExportOrder.jsp"),
    ("boundary", "gdInvoicePrint", "gdInvoicePrint.jsp"),
    ("control", "OrderDAO", "OrderDAO"),
    ("control", "OrderDetailDAO", "OrderDetailDAO"),
    ("control", "DeliveryStaffDAO", "DeliveryStaffDAO"),
    ("control", "ProductDAO", "ProductDAO"),
    ("control", "InvoiceDAO", "InvoiceDAO"),
    ("entity", "Order", "Order"),
    ("entity", "OrderDetail", "OrderDetail"),
    ("entity", "DeliveryStaff", "DeliveryStaff"),
    ("entity", "Invoice", "Invoice"),
]

V3_M2 = [
    ("A", "gdSaleHome", "click Duyệt và xuất đơn",
     "Tại trang gdSaleHome.jsp, sau khi đăng nhập, nhân viên bán hàng chọn chức năng duyệt và xuất đơn hàng."),
    ("gdSaleHome", "gdOrderList", "gọi", "Trang gdSaleHome.jsp gọi trang gdOrderList.jsp."),
    ("gdOrderList", "A", "hiển thị", "Trang gdOrderList.jsp hiển thị ô chọn trạng thái và nút Lọc."),
    ("A", "gdOrderList", "chọn Chưa xuất + click Lọc", "Nhân viên bán hàng chọn trạng thái \"Chưa xuất\" và click Lọc."),
    ("gdOrderList", "gdOrderList", "submit", "Trang gdOrderList.jsp submit gọi chính nó xử lí."),
    *fetch("gdOrderList", "OrderDAO", "getUnexportedOrder()", "Order", "lấy danh sách đơn chưa xuất"),
    ("gdOrderList", "A", "hiển thị", "Trang gdOrderList.jsp hiển thị danh sách đơn chưa xuất (DH1024, DH1025, DH1026)."),
    ("A", "gdOrderList", "click DH1024", "Nhân viên bán hàng click đơn DH1024."),
    ("gdOrderList", "gdOrderDetail", "gọi", "Trang gdOrderList.jsp gọi trang gdOrderDetail.jsp."),
    *fetch("gdOrderDetail", "OrderDetailDAO", "getOrderDetailByOrder(idOrder)", "OrderDetail",
           "lấy các dòng hàng của đơn DH1024"),
    ("gdOrderDetail", "A", "hiển thị", "Trang gdOrderDetail.jsp hiển thị chi tiết đơn DH1024 (trạng thái Chờ duyệt)."),
    ("A", "gdOrderDetail", "click Duyệt đơn", "Nhân viên bán hàng kiểm tra đơn và click Duyệt đơn."),
    ("gdOrderDetail", "doApproveOrder", "gọi", "Trang gdOrderDetail.jsp gọi trang doApproveOrder.jsp."),
    *save("doApproveOrder", "Order", "setStatus(), setSaleStaff(), setApprovedAt()", "OrderDAO",
          "approveOrder(order)", "trạng thái Đã duyệt, nhân viên duyệt và thời điểm duyệt",
          "gdOrderDetail", "Nhân viên bán hàng", "Duyệt đơn thành công"),
    ("gdOrderDetail", "A", "hiển thị", "Trang gdOrderDetail.jsp hiển thị đơn DH1024 ở trạng thái Đã duyệt."),
    ("A", "gdOrderDetail", "click Chọn NV giao hàng",
     "Nhân viên bán hàng đóng gói hàng rồi click Chọn nhân viên giao hàng."),
    ("gdOrderDetail", "gdDeliveryStaffList", "gọi", "Trang gdOrderDetail.jsp gọi trang gdDeliveryStaffList.jsp."),
    *fetch("gdDeliveryStaffList", "DeliveryStaffDAO", "getAvailableDeliveryStaff()", "DeliveryStaff",
           "lấy danh sách nhân viên giao hàng"),
    ("gdDeliveryStaffList", "A", "hiển thị", "Trang gdDeliveryStaffList.jsp hiển thị danh sách nhân viên giao hàng."),
    ("A", "gdDeliveryStaffList", "chọn GH03 + click Lưu phân công",
     "Nhân viên bán hàng chọn GH03 – Phạm Văn Dũng và click Lưu phân công."),
    ("gdDeliveryStaffList", "doSaveAssign", "gọi", "Trang gdDeliveryStaffList.jsp gọi trang doSaveAssign.jsp."),
    *save("doSaveAssign", "Order", "setDeliveryStaff()", "OrderDAO", "assignDeliveryStaff(order)",
          "nhân viên giao hàng GH03", "gdOrderDetail", "Nhân viên bán hàng", "Phân công thành công"),
    ("gdOrderDetail", "A", "hiển thị", "Trang gdOrderDetail.jsp hiển thị đơn kèm nhân viên giao hàng và nút Xác nhận xuất hàng."),
    ("A", "gdOrderDetail", "click Xác nhận xuất hàng", "Nhân viên bán hàng click Xác nhận xuất hàng."),
    ("gdOrderDetail", "doExportOrder", "gọi", "Trang gdOrderDetail.jsp gọi trang doExportOrder.jsp."),
    ("doExportOrder", "Order", "gọi",
     "Trang doExportOrder.jsp gọi lớp Order yêu cầu set trạng thái Đã xuất, nhân viên xử lí và thời điểm xuất."),
    ("Order", "Order", "setStatus(), setSaleStaff(), setExportedAt()",
     "Lớp Order gọi các hàm setStatus(), setSaleStaff(), setExportedAt()."),
    ("Order", "doExportOrder", "trả về", "Lớp Order trả đối tượng về cho trang doExportOrder.jsp."),
    ("doExportOrder", "OrderDAO", "gọi", "Trang doExportOrder.jsp gọi lớp OrderDAO yêu cầu lưu xuất đơn."),
    ("OrderDAO", "OrderDAO", "exportOrder(order)",
     "Lớp OrderDAO gọi hàm exportOrder(), mở giao dịch (setAutoCommit(false)) trên kết nối dùng chung."),
    ("OrderDAO", "ProductDAO", "gọi", "Hàm exportOrder() gọi lớp ProductDAO yêu cầu kiểm tra tồn kho."),
    ("ProductDAO", "ProductDAO", "checkStock(listDetail)", "Lớp ProductDAO gọi hàm checkStock()."),
    ("ProductDAO", "OrderDAO", "trả về", "Hàm checkStock() trả kết quả đủ tồn kho cho hàm exportOrder()."),
    ("OrderDAO", "ProductDAO", "gọi", "Hàm exportOrder() gọi lớp ProductDAO yêu cầu trừ tồn kho."),
    ("ProductDAO", "ProductDAO", "decreaseStock(listDetail)", "Lớp ProductDAO gọi hàm decreaseStock()."),
    ("ProductDAO", "OrderDAO", "trả về", "Hàm decreaseStock() trả kết quả cho hàm exportOrder()."),
    ("OrderDAO", "InvoiceDAO", "gọi", "Hàm exportOrder() gọi lớp InvoiceDAO yêu cầu lập hóa đơn."),
    ("InvoiceDAO", "InvoiceDAO", "issueInvoice(order)", "Lớp InvoiceDAO gọi hàm issueInvoice()."),
    ("InvoiceDAO", "OrderDAO", "trả về",
     "Hàm issueInvoice() trả kết quả cho hàm exportOrder(); exportOrder() commit giao dịch."),
    ("OrderDAO", "doExportOrder", "trả về", "Lớp OrderDAO trả kết quả cho trang doExportOrder.jsp."),
    ("doExportOrder", "A", "thông báo thành công", "Trang doExportOrder.jsp thông báo \"Xuất hàng thành công cho đơn DH1024\"."),
    ("A", "doExportOrder", "click OK", "Nhân viên bán hàng click OK của thông báo."),
    ("doExportOrder", "gdOrderDetail", "gọi", "Trang doExportOrder.jsp gọi lại trang gdOrderDetail.jsp."),
    ("gdOrderDetail", "A", "hiển thị", "Trang gdOrderDetail.jsp hiển thị đơn ở trạng thái Đã xuất kèm nút In hóa đơn."),
    ("A", "gdOrderDetail", "click In hóa đơn", "Nhân viên bán hàng click In hóa đơn."),
    ("gdOrderDetail", "gdInvoicePrint", "gọi", "Trang gdOrderDetail.jsp gọi trang gdInvoicePrint.jsp."),
    *fetch("gdInvoicePrint", "InvoiceDAO", "getInvoiceDetail(idInvoice, idCustomer)", "Invoice",
           "lấy dữ liệu hóa đơn HD1024"),
    ("gdInvoicePrint", "A", "hiển thị", "Trang gdInvoicePrint.jsp hiển thị bản xem trước hóa đơn HD1024."),
    ("A", "gdInvoicePrint", "click In", "Nhân viên bán hàng click In."),
    ("gdInvoicePrint", "A", "in hóa đơn",
     "Trang gdInvoicePrint.jsp gửi lệnh in; nhân viên bán hàng nhận bản in để giao cùng hàng."),
]

MODULES = {
    "track-invoice": ("q3c-3-sequence-design-track-invoice.puml", "Track Invoice 0", M1_PARTICIPANTS, V3_M1),
    "approve-export": ("q3c-4-sequence-design-approve-export.puml", "Approve and Export Order 0", M2_PARTICIPANTS, V3_M2),
}
RETURN = ("trả về", "hiển thị", "thông báo", "in hóa đơn")


def scenario_v3(module):
    """Numbered scenario v3 sentences of a module, in order."""
    return [text for _, _, _, text in MODULES[module][3]]


def emit_sequences():
    for module, (fname, uc, parts, steps) in MODULES.items():
        names = {alias for _, alias, _ in parts}
        out = ["@startuml", "!include _style.iuml", "skinparam SequenceMessageAlign left",
               f"title Thiết kế – Biểu đồ tuần tự thiết kế – {uc} ({len(steps)} bước, kịch bản v3)", ""]
        out += [f'{kind} "{label}" as {alias}' for kind, alias, label in parts]
        out.append("")
        for n, (a, b, label, _) in enumerate(steps, 1):
            assert a in names and b in names, (module, n, a, b)
            arrow = "-->" if label.startswith(RETURN) else "->"
            out.append(f"{a} {arrow} {b} : {n}: {label}")
        out.append("@enduml")
        (SRC / fname).write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"{fname}: {len(steps)} steps")


# ---------------------------------------------------------------------------------------------
# 2. Analysis communication diagrams from the analysis sequence diagrams (scenario v2).
# ---------------------------------------------------------------------------------------------
COMM = [
    ("x4-sequence-analysis-track-invoice.puml", "q3a-3-communication-track-invoice.puml",
     "Q3a – Biểu đồ giao tiếp – kịch bản chuẩn Track Invoice 0 (15 bước)"),
    ("x3-sequence-analysis-approve-export.puml", "q3a-4-communication-approve-export.puml",
     "Q3a – Biểu đồ giao tiếp – kịch bản chuẩn Approve and Export Order 0 (51 bước)"),
]


def emit_communication():
    for seq, comm, title in COMM:
        s = (SRC / seq).read_text(encoding="utf-8")
        decls = re.findall(r'^(actor|boundary|entity)\s+(?:"([^"]+)"\s+as\s+)?(\w+)', s, re.M)
        msgs = re.findall(r'^(\w+) -{1,2}> (\w+) : (\d+): (.+)$', s, re.M)
        links = {}
        for a, b, n, text in msgs:
            links.setdefault((a, b), []).append(f"{n}: {text}")
        out = ["@startuml", "!include _style.iuml", "left to right direction", f"title {title}", ""]
        out += [f'{k} "{lbl}" as {al}' if lbl else f"{k} {al}" for k, lbl, al in decls]
        out.append("")
        for (a, b), labels in links.items():
            text = "\\n".join(labels)
            out.append(f'{a} -- {b} : "{text}"' if a == b else f"{a} -- {b} : {text} >")
        out.append("@enduml")
        (SRC / comm).write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"{comm}: {len(msgs)} messages")


# ---------------------------------------------------------------------------------------------
# 3. System DB diagram from sql/system_schema.sql.
# ---------------------------------------------------------------------------------------------
MODULE_TABLES = ["tblMember", "tblCustomer", "tblStaff", "tblDeliveryStaff", "tblProductCategory", "tblProduct",
                 "tblOrder", "tblOrderDetail"]


def emit_database(fname="q4a-database-system.puml", only=None,
                  title="Thiết kế – Biểu đồ CSDL của HỆ THỐNG (sql/system_schema.sql)"):
    sql = (ROOT / "sql" / "system_schema.sql").read_text(encoding="utf-8")
    tables = re.findall(r"CREATE TABLE (\w+) \((.*?)\n\);", sql, re.S)
    if only:
        tables = [t for t in tables if t[0] in only]
    bodies = dict(tables)
    types = {"INTEGER": "integer(10)", "FLOAT": "float(10)", "DATE": "date", "DATETIME": "datetime"}
    fks = re.findall(r"CREATE TABLE (\w+) \(|CONSTRAINT \w+ FOREIGN KEY \((\w+)\) REFERENCES (\w+)", sql)
    fk_list, current = [], None
    for table, col, ref in fks:
        if table:
            current = table
        else:
            fk_list.append((current, col, ref))
    if only:
        fk_list = [f for f in fk_list if f[0] in only and f[2] in only]
    out = ["@startuml", "!include _style.iuml", "left to right direction", "skinparam linetype ortho",
           f"title {title}", ""]
    for name, body in tables:
        fkcols = {c for t, c, _ in fk_list if t == name}
        rows = []
        for line in body.strip().splitlines():
            line = line.split("--")[0].strip().rstrip(",")
            if not line or line.startswith("CONSTRAINT"):
                continue
            col, typ, rest = re.match(r"(\w+)\s+(\w+(?:\(\d+\))?)(.*)", line).groups()
            typ = types.get(typ, typ.lower())
            if "PRIMARY KEY" in rest:
                rows.insert(0, f"  * {col} : {typ} {'<<PK, FK>>' if col in fkcols else '<<PK>>'}\n  --")
            else:
                tag = " <<FK>>" if col in fkcols else (" <<U>>" if "UNIQUE" in rest else "")
                rows.append(f"  {'* ' if 'NOT NULL' in rest else ''}{col} : {typ}{tag}")
        out += [f"entity {name} {{", *rows, "}"]
    out.append("")
    for t, c, ref in fk_list:
        if re.search(rf"^\s+{c}\s+\w+\s+NOT NULL PRIMARY KEY", bodies[t], re.M):
            out.append(f"{ref} ||--|| {t}")
        elif re.search(rf"^\s+{c}\s+\w+\s+NOT NULL", bodies[t], re.M):
            out.append(f"{ref} ||--o{{ {t}")
        else:
            out.append(f"{ref} |o--o{{ {t}")
    out.append("@enduml")
    (SRC / fname).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{fname}: {len(tables)} tables, {len(fk_list)} FKs")


if __name__ == "__main__":
    emit_sequences()
    emit_communication()
    emit_database()
    emit_database("q4a-2-database-two-modules.puml", MODULE_TABLES,
                  "Q4a – CSDL liên quan đến hai module (tập con của CSDL hệ thống)")
