#!/usr/bin/env python3
"""Draw every report diagram in Visual Paradigm (through the VP MCP plugin) and export it as PNG.

The content comes from the same single sources as the PlantUML versions, so the two can never drift:
  - diagrams/src/*.puml           use case, class, state, activity, package, deployment, analysis sequences
  - diagrams/generate.py          scenario v3 (design sequences), communication = analysis sequence messages
  - sql/system_schema.sql         database diagrams

Needs Visual Paradigm (Community Edition for clean exports) running with the MCP plugin on :2026.
  python3 build_vp.py              build all diagrams into vp/TXTHANH.vpp and export diagrams/out/vp/*.png
  python3 build_vp.py q1a-2 x5     only these keys (prefix match); existing diagrams with the same name are skipped
  python3 build_vp.py --export     only re-export
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "diagrams" / "src"
OUT = ROOT / "diagrams" / "out" / "vp"
VPP = ROOT / "vp" / "TXTHANH.vpp"
sys.path.insert(0, str(ROOT / "diagrams"))
import generate  # noqa: E402


# ------------------------------------------------------------------ VP client
def call(tool, **args):
    body = json.dumps({"toolName": tool, "arguments": args}).encode()
    req = urllib.request.Request("http://localhost:2026/api/execute", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode())
    if "error" in data:
        raise RuntimeError(f"{tool}({args}): {data['error']}")
    out = data.get("result", "")
    low = out.lower()
    if low.startswith(("error", "unknown")) or "not found" in low[:200] or "failed" in low[:120]:
        raise RuntimeError(f"{tool}({args}) -> {out}")
    return out


def one_line(s):
    return re.sub(r"\s*\\n\s*", " ", s).strip()


def uniq_name(name, used):
    """Activity/state handles must be unique; duplicates get zero-width spaces (invisible)."""
    n = name
    while n in used:
        n += "​"
    used.add(n)
    return n


def read(name):
    text = (SRC / name).read_text(encoding="utf-8")
    text = re.sub(r"^!include (\S+)$", lambda m: (SRC / m.group(1)).read_text(encoding="utf-8")
                  if m.group(1) != "_style.iuml" else "", text, flags=re.M)
    return [l.rstrip() for l in text.splitlines() if l.strip() and not l.strip().startswith("'")]


# ------------------------------------------------------------------ use case
def use_case(key, src, d):
    lines = read(src)
    names, actors, ucs, rels, system = {}, [], [], [], ""
    for l in lines:
        s = l.strip()
        if m := re.match(r'actor\s+(?:"([^"]+)"\s+as\s+(\w+)|(\w+))', s):
            label, alias = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(3))
            names[alias] = label
            actors.append(label)
        elif m := re.match(r'usecase\s+"([^"]+)"\s+as\s+(\w+)', s):
            names[m.group(2)] = m.group(1)
            ucs.append(m.group(1))
        elif m := re.match(r'rectangle\s+"([^"]+)"', s):
            system = m.group(1)
        elif m := re.match(r'(\w+)\s+(-+(?:up-)?\|>|-+|\.+>)\s+(\w+)(?:\s*:\s*(.*))?$', s):
            a, arrow, b, label = m.groups()
            kind = ("Generalization" if arrow.endswith("|>") else
                    "Association" if arrow.startswith("-") else
                    "Include" if "include" in (label or "") else "Extend")
            rels.append((kind, a, b))
    call("createUseCaseDiagram", diagramName=d)
    for a in actors:
        call("addActor", actorName=a, diagramName=d, x=0, y=0)
    for u in ucs:
        call("addUseCase", useCaseName=u, diagramName=d, x=0, y=0)
    order = {"Include": 0, "Extend": 1, "Generalization": 2, "Association": 3}
    for kind, a, b in sorted(rels, key=lambda r: order[r[0]]):
        # PlantUML "Detail ..> List : <<extend>>": Detail extends List -> source = extension, target = base
        call("addRelationship", diagramName=d, sourceName=names[a], targetName=names[b], relationshipType=kind)
    call("addSystemBoundary", diagramName=d, systemName=system)


def white_classes(key, src, d):
    """Course sample class diagrams use plain white boxes."""
    classes, _ = parse_classes(src)
    for c in classes.values():
        call("setClassColor", diagramName=d, className=c["name"], backgroundColor="#FFFFFF")


# ------------------------------------------------------------------ class
def parse_classes(src):
    lines = read(src)
    classes, rels, cur = {}, [], None
    for l in lines:
        s = l.strip()
        if cur is not None:
            if s == "}":
                cur = None
            else:
                classes[cur]["members"].append(s)
            continue
        if m := re.match(r'(?:abstract\s+)?class\s+(?:"([^"]+)"\s+as\s+(\w+)|(\w+))(?:\s*<<\w+>>)?\s*(\{)?', s):
            label, alias = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(3))
            classes[alias] = {"name": label, "members": []}
            cur = alias if m.group(4) else None
        elif s.startswith("enum "):
            cur = "__skip__"
            classes[cur] = {"name": "", "members": []}
        elif m := re.match(r'(\w+)\s+(?:"([^"]+)"\s+)?([-.*o|<>a-z\[\]]+)\s+(?:"([^"]+)"\s+)?(\w+)(?:\s*:\s*(.*))?$', s):
            a, ma, arrow, mb, b, label = m.groups()
            if "hidden" in arrow or a not in classes or b not in classes:
                continue
            label = (label or "").rstrip("> ").strip()
            if arrow.endswith("|>"):
                rels.append(("gen", a, b, "", "", ""))
            elif arrow.startswith("*"):
                rels.append(("comp", a, b, ma or "", mb or "", ""))
            elif arrow.startswith("o"):
                rels.append(("aggr", a, b, ma or "", mb or "", ""))
            elif arrow.endswith(">"):
                rels.append(("dep", a, b, "", "", ""))
            else:
                rels.append(("assoc", a, b, ma or "", mb or "", label))
    classes.pop("__skip__", None)
    return classes, rels


VIS = {"-": "private", "+": "public", "#": "protected", "~": "package"}


def class_diagram(key, src, d):
    classes, rels = parse_classes(src)
    call("createClassDiagram", diagramName=d)
    # tiers: JSP/View on top, DAO in the middle, entities below (pinned rows, like the book)
    gens = {a: b for k, a, b, *_ in rels if k == "gen"}
    for alias, c in classes.items():
        call("addClass", diagramName=d, className=c["name"], packageName="", packageColor="", stereotype="",
             isAbstract=False, extendsClass="", implementsInterfaces="", x=0, y=0, modelPackage=key)
        for mem in c["members"]:
            vis = VIS.get(mem[0], "private")
            body = mem[1:] if mem[0] in VIS else mem
            body = body.replace("{static}", "").strip()
            if "(" in body:
                name, params, ret = re.match(r"(\w+)\((.*)\)\s*(?::\s*(.+))?$", body).groups()
                params = ", ".join(re.sub(r"\s*:\s*", ": ", p.strip()) for p in params.split(",") if p.strip())
                call("addOperation", className=c["name"], operationName=name, returnType=(ret or "").strip(),
                     params=params, visibility=vis, isAbstract=False, diagramName=d)
            else:
                name, _, typ = body.partition(":")
                call("addAttribute", className=c["name"], attributeName=name.strip(), attributeType=typ.strip(),
                     visibility=vis, diagramName=d)
    n = lambda a: classes[a]["name"]
    for kind, a, b, ma, mb, label in rels:
        if kind == "gen":
            call("addGeneralization", diagramName=d, fromClass=n(a), toClass=n(b))
        elif kind == "comp":
            call("addComposition", diagramName=d, fromClass=n(a), toClass=n(b), fromMultiplicity=ma, toMultiplicity=mb)
        elif kind == "aggr":
            call("addAggregation", diagramName=d, fromClass=n(a), toClass=n(b), fromMultiplicity=ma, toMultiplicity=mb)
        elif kind == "dep":
            call("addDependency", diagramName=d, fromClass=n(a), toClass=n(b))
        else:
            call("addAssociation", diagramName=d, fromClass=n(a), toClass=n(b), fromMultiplicity=ma,
                 toMultiplicity=mb, name=label)
    # only one-way arrows where PlantUML had none: association ends stay unspecified (no arrow heads)
    for kind, a, b, ma, mb, label in rels:
        if kind in ("assoc", "aggr", "comp"):
            call("setAssociationProperties", diagramName=d, fromClass=n(a), toClass=n(b), name="",
                 fromMultiplicity="", toMultiplicity="", fromRole="-", toRole="-",
                 fromNavigable="unspecified", toNavigable="unspecified")
    call("autoLayoutDiagram", diagramName=d)
    white_classes(key, src, d)


# ------------------------------------------------------------------ sequence
def parse_seq(src):
    lines = read(src)
    parts, msgs = [], []
    for l in lines:
        s = l.strip()
        if m := re.match(r'(actor|boundary|control|entity)\s+(?:"([^"]+)"\s+as\s+(\w+)|(\w+))', s):
            kind = m.group(1)
            label, alias = (m.group(2), m.group(3)) if m.group(2) else (m.group(4), m.group(4))
            parts.append((kind, alias, label))
        elif m := re.match(r'(\w+)\s+(-->|->)\s+(\w+)\s*:\s*(\d+):\s*(.+)$', s):
            msgs.append((m.group(1), m.group(3), m.group(5).strip(), m.group(2) == "-->", m.group(4)))
    return parts, msgs


def sequence(d, parts, msgs):
    call("createSequenceDiagram", diagramName=d)
    label = {alias: lbl for _, alias, lbl in parts}
    for kind, alias, lbl in parts:
        call("addLifeline", diagramName=d, lifelineName=lbl, className="", lifelineType=kind, alias="")
    for a, b, text, ret, n in msgs:
        if ret:
            call("addReturnMessage", diagramName=d, fromLifeline=label[a], toLifeline=label[b],
                 messageName=text, sequenceNumber=str(n))
        else:
            call("addMessage", diagramName=d, fromLifeline=label[a], toLifeline=label[b], messageName=text,
                 sequenceNumber=str(n), messageType="sync")


def seq_analysis(key, src, d):
    sequence(d, *parse_seq(src))


def seq_design(key, module, d):
    _, _, parts, steps = generate.MODULES[module]
    msgs = [(a, b, label, label.startswith(generate.RETURN), i) for i, (a, b, label, _) in enumerate(steps, 1)]
    sequence(d, parts, msgs)


# ------------------------------------------------------------------ communication
def communication(key, src, d):
    parts, msgs = parse_seq(src)
    label = {alias: lbl for _, alias, lbl in parts}
    call("createCommunicationDiagram", diagramName=d)
    for kind, alias, lbl in parts:
        call("addCommunicationLifeline", diagramName=d, lifelineName=lbl, classifierName="",
             isActor=kind == "actor", x=0, y=0, lifelineType="" if kind == "actor" else kind)
    for a, b, text, ret, n in msgs:
        call("addCommunicationMessage", diagramName=d, fromLifeline=label[a], toLifeline=label[b],
             sequenceNumber=str(n), messageText=text)


# ------------------------------------------------------------------ state
def state(key, src, d):
    lines = read(src)
    names, trans = {}, []
    for l in lines:
        s = l.strip()
        if m := re.match(r'state\s+"([^"]+)"\s+as\s+(\w+)', s):
            names[m.group(2)] = m.group(1)
        elif m := re.match(r'(\[\*\]|\w+)\s+-+>\s+(\[\*\]|\w+)(?:\s*:\s*(.*))?$', s):
            trans.append((m.group(1), m.group(2), one_line(m.group(3) or "")))
    call("createStateDiagram", diagramName=d)
    call("addInitialState", diagramName=d, stateName="Bắt đầu", x=0, y=0)
    for a, b, _ in trans:
        for s in (a, b):
            if s != "[*]" and s not in names:
                names[s] = s
    for alias, lbl in names.items():
        call("addState", diagramName=d, stateName=lbl, entryAction="", doActivity="", exitAction="", x=0, y=0)
    call("addFinalState", diagramName=d, stateName="Kết thúc", x=0, y=0)
    for a, b, lbl in trans:
        lbl = lbl.replace("Bắt đầu ", "").replace(" Kết thúc", "").strip()
        fa = "Bắt đầu" if a == "[*]" else names[a]
        fb = "Kết thúc" if b == "[*]" else names[b]
        call("addTransition", diagramName=d, fromState=fa, toState=fb, label=lbl)
    call("autoLayoutDiagram", diagramName=d)


# ------------------------------------------------------------------ activity (book style: frame per page)
def parse_activity(src):
    lines = read(src)
    used, names, frames, flows, daos, frame = set(), {}, [], [], [], None
    for l in lines:
        s = l.strip()
        if m := re.match(r'partition\s+"([^"]+)"', s):
            frame = (m.group(1), [])
            frames.append(frame)
            continue
        if s == "}":
            frame = None
            continue
        if m := re.match(r'(\(\*\)|\w+)\s+\.>\s+"([^"]+)"\s+as\s+(\w+)', s):
            names[m.group(3)] = uniq_name(one_line(m.group(2)), used)
            daos.append((m.group(1), m.group(3)))
            continue
        m = re.match(r'(\(\*\)|\w+)\s+-->(?:\[([^\]]+)\])?\s+(?:"([^"]+)"\s+as\s+(\w+)|(\(\*\)|\w+))$', s)
        if not m:
            continue
        a, guard, lbl, alias, target = m.groups()
        if lbl:
            # frame members are passed comma-separated, so an action name must not contain ", "
            names[alias] = uniq_name(one_line(lbl).replace(", ", " và ").replace(",", " và"), used)
            if frame:
                frame[1].append(alias)
            target = alias
        flows.append((a, target, one_line(guard or "")))
    names["START"], names["END"] = "Bắt đầu", "Kết thúc"
    return names, frames, flows, daos


# Pinned layout (top-left x, y) for diagrams the automatic layout leaves tangled.
# Book style: one rounded frame per page, the DAO call boxes just below the frame.
ACTIVITY_LAYOUT = {
    "q3c-2-activity-approve-export": {
        "START": (130, 80), "H1": (60, 160), "H2": (60, 240),
        "L0": (420, 80), "L1": (420, 160), "L2": (420, 240), "X1": (400, 350),
        "D1": (760, 80), "D2": (760, 160), "D3": (760, 240), "X2": (740, 350),
        "P1": (1120, 80), "P2": (1120, 160), "P3": (1120, 240), "X7": (1100, 350), "END": (1420, 245),
        "A1": (60, 520), "A2": (60, 600), "A3": (60, 680), "X3": (40, 790),
        "G1": (420, 520), "G2": (420, 600), "X4": (400, 790),
        "S1": (760, 520), "S2": (760, 600), "S3": (760, 680), "X5": (740, 790),
        "E1": (1120, 520), "E2": (1120, 600), "E3": (1120, 680), "E4": (1300, 680), "X6": (1500, 600),
    },
}


def relayout(d, names, layout):
    for alias, (x, y) in layout.items():
        call("setElementBounds", diagramName=d, elementName=names[alias], x=x, y=y, width=0, height=0)


def activity_frames(d, names, frames, flows):
    has_start = any(a == "(*)" for a, *_ in flows)
    for title, members in frames:
        nodes = [names[m] for m in members]
        if title == frames[0][0] and has_start:
            nodes.insert(0, "Bắt đầu")
        call("addActivityFrame", diagramName=d, title=title, nodeNames=",".join(nodes), x=0, y=0, width=0, height=0)


def activity(key, src, d):
    names, frames, flows, daos = parse_activity(src)
    layout = ACTIVITY_LAYOUT.get(key, {})
    pos = lambda alias: layout.get(alias, (0, 0))
    call("createActivityDiagram", diagramName=d)
    has_start = any(a == "(*)" for a, *_ in flows)
    has_end = any(b == "(*)" for _, b, _ in flows)
    if has_start:
        x, y = pos("START")
        call("addActivityControlNode", diagramName=d, kind="initial", nodeName="Bắt đầu", partitionName="", x=x, y=y)
    for alias, lbl in names.items():
        if alias in ("START", "END"):
            continue
        x, y = pos(alias)
        call("addActivityAction", diagramName=d, actionName=lbl, partitionName="", x=x, y=y)
    if has_end:
        x, y = pos("END")
        call("addActivityControlNode", diagramName=d, kind="final", nodeName="Kết thúc", partitionName="", x=x, y=y)
    for a, b, guard in flows:
        fa = "Bắt đầu" if a == "(*)" else names[a]
        fb = "Kết thúc" if b == "(*)" else names[b]
        call("addActivityFlow", diagramName=d, fromNode=fa, toNode=fb, guard=guard, twoWay=False)
    for a, x in daos:
        call("addActivityFlow", diagramName=d, fromNode=names[a], toNode=names[x], guard="", twoWay=True)
    if layout:
        relayout(d, names, layout)
    activity_frames(d, names, frames, flows)
    if layout:
        call("rerouteConnectors", diagramName=d)


def fix_activity(key, src, d):
    """Re-pin an already built activity diagram and refit its frames."""
    names, frames, flows, _ = parse_activity(src)
    relayout(d, names, ACTIVITY_LAYOUT[key])
    activity_frames(d, names, frames, flows)
    call("rerouteConnectors", diagramName=d)


# ------------------------------------------------------------------ database
def database(key, only, d):
    sql = (ROOT / "sql" / "system_schema.sql").read_text(encoding="utf-8")
    tables = re.findall(r"CREATE TABLE (\w+) \((.*?)\n\);", sql, re.S)
    if only:
        tables = [t for t in tables if t[0] in only]
    keep = {t for t, _ in tables}
    call("createErd", diagramName=d)
    fks = []
    for name, body in tables:
        call("addTable", diagramName=d, tableName=name)
        for line in body.strip().splitlines():
            line = line.split("--")[0].strip().rstrip(",")
            if not line:
                continue
            if m := re.match(r"CONSTRAINT \w+ FOREIGN KEY \((\w+)\) REFERENCES (\w+)", line):
                if m.group(2) in keep:
                    fks.append((name, m.group(2), m.group(1)))
                continue
            if line.startswith("CONSTRAINT"):
                continue
            col, typ, length, rest = re.match(r"(\w+)\s+(\w+)(?:\((\d+)\))?(.*)", line).groups()
            typ = typ.lower()
            length = int(length) if length else (10 if typ in ("integer", "float") else 0)
            if only:  # tables already built by the system ERD: same name = same table, reuse its columns
                continue
            call("addColumn", diagramName=d, tableName=name, columnName=col, columnType=typ, length=length,
                 scale=0, isPrimaryKey="PRIMARY KEY" in rest, isNullable="NOT NULL" not in rest,
                 isUnique="UNIQUE" in rest)
    for child, parent, col in fks:
        try:
            call("addForeignKey", diagramName=d, fromTable=child, toTable=parent, fromColumn=col, toColumn="",
                 relationshipName="")
        except RuntimeError as e:
            if "already" not in str(e):
                raise
    call("autoLayoutDiagram", diagramName=d)


# ------------------------------------------------------------------ package (book Hình 4.15)
def package(key, src, d):
    call("createPackageDiagram", diagramName=d)
    call("addPackageElement", diagramName=d, packageName="view", parentPackage="", x=0, y=0, width=0, height=0,
         backgroundColor="")
    groups = {
        "thanhvien": ["gdLogin.jsp", "doLogin.jsp"],
        "khachhang": ["gdCustomerHome.jsp", "gdInvoiceList.jsp", "gdInvoiceDetail.jsp"],
        "nhanvienbanhang": ["gdSaleHome.jsp", "gdOrderList.jsp", "gdOrderDetail.jsp", "gdDeliveryStaffList.jsp",
                            "gdInvoicePrint.jsp", "doApproveOrder.jsp", "doSaveAssign.jsp", "doExportOrder.jsp"],
    }
    for sub, pages in groups.items():
        call("addPackageElement", diagramName=d, packageName=sub, parentPackage="view", x=0, y=0, width=0, height=0,
             backgroundColor="")
        for p in pages:
            call("addClassInPackage", diagramName=d, packageName=sub, className=p)
    for pkg, classes in (("dao", ["DAO", "MemberDAO", "InvoiceDAO", "OrderDAO", "OrderDetailDAO", "ProductDAO",
                                  "DeliveryStaffDAO"]),
                         ("model", ["Member", "Customer", "Staff", "SaleStaff", "Order", "OrderDetail", "Product",
                                    "DeliveryStaff", "Invoice"])):
        call("addPackageElement", diagramName=d, packageName=pkg, parentPackage="", x=0, y=0, width=0, height=0,
             backgroundColor="")
        for c in classes:
            call("addClassInPackage", diagramName=d, packageName=pkg, className=c)
    call("addPackageDependency", diagramName=d, fromPackage="view", toPackage="dao", kind="line")
    call("addPackageDependency", diagramName=d, fromPackage="dao", toPackage="model", kind="line")


# ------------------------------------------------------------------ deployment (MVC on J2EE)
def deployment(key, src, d):
    N = lambda name, kind, parent="": call("addDeploymentNode", diagramName=d, nodeName=name, kind=kind,
                                           parentNode=parent, x=0, y=0, width=0, height=0)
    call("createDeploymentDiagram", diagramName=d)
    N("Máy khách (PC / điện thoại)", "device")
    N("Trình duyệt web", "executionEnvironment", "Máy khách (PC / điện thoại)")
    call("addDeploymentArtifact", diagramName=d, artifactName="HTML / CSS / JS (trang do JSP sinh ra)",
         nodeName="Trình duyệt web", x=0, y=0)
    N("Web Server", "device")
    N("Apache Tomcat 10+ (Jakarta EE)", "executionEnvironment", "Web Server")
    call("addDeploymentArtifact", diagramName=d, artifactName="deptstore.war", nodeName="Apache Tomcat 10+ (Jakarta EE)",
         x=0, y=0)
    for c in ("View: gd*.jsp", "Controller: do*.jsp + dao", "Model: model"):
        call("addDeploymentComponent", diagramName=d, componentName=c, nodeName="deptstore.war", x=0, y=0)
    call("addDeploymentArtifact", diagramName=d, artifactName="mysql-connector-j.jar", nodeName="deptstore.war",
         x=0, y=0)
    N("Database Server", "device")
    N("MySQL 8", "executionEnvironment", "Database Server")
    call("addDeploymentArtifact", diagramName=d, artifactName="deptstore (11 bảng tbl*)", nodeName="MySQL 8", x=0, y=0)
    N("Máy in hóa đơn", "device")
    call("addCommunicationPath", diagramName=d, fromNode="Máy khách (PC / điện thoại)", toNode="Web Server",
         label="1: HTTP/HTTPS (8080/443)")
    call("addCommunicationPath", diagramName=d, fromNode="Web Server", toNode="Database Server",
         label="2: JDBC / TCP 3306")
    call("addCommunicationPath", diagramName=d, fromNode="Máy khách (PC / điện thoại)", toNode="Máy in hóa đơn",
         label="3: in hóa đơn (window.print())")
    call("addDeploymentDependency", diagramName=d, fromElement="View: gd*.jsp", toElement="Controller: do*.jsp + dao",
         label="submit form")
    call("addDeploymentDependency", diagramName=d, fromElement="Controller: do*.jsp + dao", toElement="Model: model",
         label="đóng gói thực thể")
    call("addDeploymentDependency", diagramName=d, fromElement="Controller: do*.jsp + dao",
         toElement="mysql-connector-j.jar", label="JDBC")


# ------------------------------------------------------------------ catalogue: key = PNG name used by the report
DIAGRAMS = [
    ("q1a-1-usecase-overview", "UC tong quan", use_case, "q1a-1-usecase-overview.puml"),
    ("q1a-2-usecase-track-invoice", "UC module 1 Theo doi hoa don", use_case, "q1a-2-usecase-track-invoice.puml"),
    ("q1a-3-usecase-approve-export", "UC module 2 Duyet va xuat don", use_case, "q1a-3-usecase-approve-export.puml"),
    ("q2b-entity-classes", "Lop thuc the hai module", class_diagram, "q2b-entity-classes.puml"),
    ("x2-state-order", "Trang thai Order", state, "x2-state-order.puml"),
    ("q3a-1-analysis-classes-track-invoice", "Lop phan tich module 1", class_diagram,
     "q3a-1-analysis-classes-track-invoice.puml"),
    ("x5-state-screen-track-invoice", "Trang thai GD module 1", state, "x5-state-screen-track-invoice.puml"),
    ("q3a-3-communication-track-invoice", "Giao tiep module 1", communication, "x4-sequence-analysis-track-invoice.puml"),
    ("x4-sequence-analysis-track-invoice", "Tuan tu phan tich module 1", seq_analysis,
     "x4-sequence-analysis-track-invoice.puml"),
    ("q3a-2-analysis-classes-approve-export", "Lop phan tich module 2", class_diagram,
     "q3a-2-analysis-classes-approve-export.puml"),
    ("x6-state-screen-approve-export", "Trang thai GD module 2", state, "x6-state-screen-approve-export.puml"),
    ("q3a-4-communication-approve-export", "Giao tiep module 2", communication,
     "x3-sequence-analysis-approve-export.puml"),
    ("x3-sequence-analysis-approve-export", "Tuan tu phan tich module 2", seq_analysis,
     "x3-sequence-analysis-approve-export.puml"),
    ("q2c-design-entity-classes-system", "Lop thuc the thiet ke he thong", class_diagram,
     "q2c-design-entity-classes-system.puml"),
    ("q4a-database-system", "CSDL he thong", database, None),
    ("q4a-2-database-two-modules", "CSDL hai module", database, generate.MODULE_TABLES),
    ("q3b-3-design-classes-track-invoice", "Lop thiet ke module 1", class_diagram,
     "q3b-3-design-classes-track-invoice.puml"),
    ("q3c-1-activity-track-invoice", "Hoat dong module 1", activity, "q3c-1-activity-track-invoice.puml"),
    ("q3c-3-sequence-design-track-invoice", "Tuan tu thiet ke module 1", seq_design, "track-invoice"),
    ("q3b-4-design-classes-approve-export", "Lop thiet ke module 2", class_diagram,
     "q3b-4-design-classes-approve-export.puml"),
    ("q3c-2-activity-approve-export", "Hoat dong module 2", activity, "q3c-2-activity-approve-export.puml"),
    ("q3c-4-sequence-design-approve-export", "Tuan tu thiet ke module 2", seq_design, "approve-export"),
    ("q5a-package", "Bieu do goi", package, None),
    ("q5b-deployment", "Bieu do trien khai", deployment, None),
]


def main(argv):
    export_only = "--export" in argv
    keys = [a for a in argv if not a.startswith("--")]
    info = json.loads(call("getProjectInfo"))
    if info.get("file") != str(VPP):
        if VPP.exists():
            call("openProject", filePath=str(VPP))
        else:
            VPP.parent.mkdir(exist_ok=True)
            call("saveProjectAs", filePath=str(VPP))
    try:
        existing = call("listDiagrams", type="")
    except RuntimeError:
        existing = ""
    OUT.mkdir(parents=True, exist_ok=True)
    for key, d, fn, arg in DIAGRAMS:
        if keys and not any(key.startswith(k) for k in keys):
            continue
        if not export_only and d not in existing:
            print("build ", key, flush=True)
            fn(key, arg, d)
            call("saveProject")
        call("exportDiagramImage", diagramName=d, filePath=str(OUT / f"{key}.png"))
        print("export", key, flush=True)
    call("saveProject")


if __name__ == "__main__":
    main(sys.argv[1:])
