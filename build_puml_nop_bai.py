#!/usr/bin/env python3
"""Flatten the PlantUML sources answering each Google Form into self-contained files (no !include),
ready to paste: puml_nop_bai/<form>/<n>_<name>.puml. Run after editing diagrams/src."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "diagrams" / "src"
OUT = ROOT / "puml_nop_bai"
FORMS = {
    "1_dac-ta": [
        ("1_Use-case-tong-quan-he-thong", "q1a-1-usecase-overview"),
        ("2_Use-case-chi-tiet_module-1_Khach-hang-theo-doi-hoa-don", "q1a-2-usecase-track-invoice"),
        ("3_Use-case-chi-tiet_module-2_NV-ban-hang-duyet-don-xuat-hang", "q1a-3-usecase-approve-export"),
    ],
    "2_phan-tich": [
        ("1_So-do-lop-thuc-the", "q2b-entity-classes"),
        ("2_So-do-lop-phan-tich_module-1_Khach-hang-theo-doi-hoa-don", "q3a-1-analysis-classes-track-invoice"),
        ("3_So-do-lop-phan-tich_module-2_NV-ban-hang-duyet-don-xuat-hang", "q3a-2-analysis-classes-approve-export"),
        ("4_Communication-diagram_module-1_Khach-hang-theo-doi-hoa-don", "q3a-3-communication-track-invoice"),
        ("5_Communication-diagram_module-2_NV-ban-hang-duyet-don-xuat-hang", "q3a-4-communication-approve-export"),
    ],
    "3_thiet-ke": [
        ("1_So-do-lop-thuc-the_pha-thiet-ke", "q2c-design-entity-classes-system"),
        ("2_So-do-thiet-ke-CSDL", "q4a-database-system"),
        ("3_So-do-lop-thiet-ke_module-1_Khach-hang-theo-doi-hoa-don", "q3b-3-design-classes-track-invoice"),
        ("4_So-do-lop-thiet-ke_module-2_NV-ban-hang-duyet-don-xuat-hang", "q3b-4-design-classes-approve-export"),
        ("5_Sequence-diagram_module-1_Khach-hang-theo-doi-hoa-don", "q3c-3-sequence-design-track-invoice"),
        ("6_Sequence-diagram_module-2_NV-ban-hang-duyet-don-xuat-hang", "q3c-4-sequence-design-approve-export"),
    ],
}
INCLUDE = re.compile(r"^(\s*)!include\s+(\S+)\s*$")


def flatten(path: Path) -> list[str]:
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = INCLUDE.match(line)
        if m:
            lines += [m.group(1) + l for l in flatten(path.parent / m.group(2)) if l.strip() not in ("@startuml", "@enduml")]
        else:
            lines.append(line)
    return lines


def main() -> None:
    for form, items in FORMS.items():
        (OUT / form).mkdir(parents=True, exist_ok=True)
        for name, src in items:
            text = "\n".join(flatten(SRC / f"{src}.puml")) + "\n"
            assert "!include" not in text
            (OUT / form / f"{name}.puml").write_text(text, encoding="utf-8")
            print(f"{form}/{name}.puml  <- {src}.puml")


if __name__ == "__main__":
    main()
