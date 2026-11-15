# TXTHANH – Online Department Store (two modules)

Answer to [question.md](question.md): **Customer tracks invoice** and **Sale staff approves orders + export**.
The work comes from `../cnpm-hrm` (report `34_B23DCAT280.docx`, git history v1–v3, and `docs/uc-sale-approve-export.md`). It was checked against the question, corrected, completed for Q3–Q5, and every diagram was redrawn in PlantUML.

## Run the app

```bash
python3 run_app.py        # Java 17+; compiles java/, starts embedded Tomcat on http://localhost:8080/gdLogin.jsp
```

It builds an SQLite database from `sql/system_schema.sql` + `sql/system_sample_data.sql` (the data of both standard scenarios), so neither MySQL nor a Tomcat install is needed. Accounts: customer `an` / `123456` (module 1), sale staff `lan` / `123456` (module 2). Production target is MySQL: `dao/DAO.java` reads `-Ddeptstore.db.url/.user/.password`.

Screens of both standard scenarios, captured from the running app: [screenshots/app/](screenshots/app/). PlantUML handed in through the course forms (self-contained, no `!include`): [puml_nop_bai/](puml_nop_bai/), rebuilt by [build_puml_nop_bai.py](build_puml_nop_bai.py).

The Word reports (`*.docx`), `source/`, `versions/`, `submission_ready/` and `legacy/` stay local and are not in this repository.

## Contents

| Path | What it is |
|---|---|
| [answer.md](answer.md) | **The answer, Q1a → Q5b** (Vietnamese, like the original report) |
| `34_B23DCAT280_v8_2026-11-15_ban-cuoi.docx` (local, also PDF in `submission_ready/Ban_cuoi/`) | **Final report**: cover page, A4, page numbers, then the four parts the course asks for: PHẦN I Đặc tả, II Phân tích, III Thiết kế, IV Lập trình (incl. 8.4 screens of the running app, 8.5 project tree as two VS Code Explorer columns, 8.6 this repository) + Phụ lục A versions, B replaced figures, C prompts grouped by task and how each result was used, D references. Every UML figure is the Visual Paradigm CE export. Built by `build_docx.py --vp` then [build_full_docx.py](build_full_docx.py) (v7 of 14/11 is in `versions/`) |
| [build_vp.py](build_vp.py) | Draws all 24 report diagrams in Visual Paradigm through the VP MCP plugin, from the same sources as the PlantUML ones (`diagrams/src`, `diagrams/generate.py`, `sql/system_schema.sql`), into [vp/TXTHANH.vpp](vp/), and exports [diagrams/out/vp/](diagrams/out/vp/) |
| [34_B23DCAT280_v6_2026-10-27_tong-hop.docx](34_B23DCAT280_v6_2026-10-27_tong-hop.docx) | **Consolidated report (all versions):** v5 content + table of contents + Phụ lục A version history + Phụ lục B figures replaced in earlier versions. Built by [build_full_docx.py](build_full_docx.py). Uploaded to Google Docs: [B23DCAT280 - CNPM / 34_B23DCAT280_v6_2026-10-27_tong-hop](https://docs.google.com/document/d/1X3uv9500OozkGKmP_BlwAG16rolcmET7Dj6WA3Jn3z0/edit) (private, personal Drive) |
| [34_B23DCAT280_v5_2026-10-26_day-du.docx](34_B23DCAT280_v5_2026-10-26_day-du.docx) | Latest full report: analysis (1–6), design (7), implementation (8). Built by [build_docx.py](build_docx.py) from the v3 original |
| [versions/](versions/) | Earlier versions with distinct names: v1, v2 (cnpm-hrm git history), v4 (12/10 full report). v3 is in `source/`, v4/v5 design submissions in `submission_ready/` |
| [source/](source/) | Original artifacts: untouched cnpm-hrm report `34_B23DCAT280_v3_2026-09-21_cnpm-hrm-goc.docx`, module 2 analysis markdown, VP project `b23dcat280.vpp`, VP/PlantUML images in `vp_images/` |
| [diagrams/generate.py](diagrams/generate.py) | Single source of scenario v3; generates the design sequence diagrams, the analysis communication diagrams and the system DB diagram |
| [diagrams/src/](diagrams/src/) | 36 PlantUML sources: `q1a…q5b` by question (incl. `q2c` system design entities, `q3b-*-ui-*` wireframes, `q3b-3/4` JSP+DAO design classes, `q3c` activity + design sequences, `q4a-database-system`); `x…` appendix analysis extras; `z…` legacy Servlet design that goes with the prototype Java |
| [diagrams/out/](diagrams/out/) | Exported `png/` and `svg/` |
| [export_diagrams.py](export_diagrams.py) | Diagram exporter |
| [sql/](sql/) | Q4a: `system_schema.sql` (system DB, 11 tables) and `system_sample_data.sql` (data of both scenarios) |
| [java/](java/) | Q4b, textbook layout: `src/model` (JavaBeans), `src/dao` (`DAO` base + `XxxDAO extends DAO`), `WebContent` (JSP: `gdLogin`/`doLogin`, `khachhang/`, `nhanvienbanhang/`), `test` (JUnit per DAO + embedded-Tomcat web flow) |
| [legacy/](legacy/) | Earlier Servlet-style prototype and its two-module DB; superseded, not maintained or verified |
| [verify.py](verify.py) | End-to-end verification |
| [DANH_GIA_DIEM.md](DANH_GIA_DIEM.md) | Self-assessed score for all 5 questions, graded under CNPM 2020, short bullets |
| [submission_ready/](submission_ready/) | Files to hand in: full report, `Thiet_ke_1` (7.1–7.2 + UI + module classes), `Thiet_ke_2` (activity, v3, sequence), `Thiet_ke_3` (whole design phase incl. package + deployment) |
| [REVIEW_BG_CNPM_2020.md](REVIEW_BG_CNPM_2020.md) | Review of this work against the course book `BG HP TTTN 2 CNPM 2020` (findings H/M/L with page references) |
| [cnpm-skill-nuances.md](cnpm-skill-nuances.md) | Book conventions checked against the `cnpm` skill (covered / partial / missing / conflicting) + proposed skill edits |

## Commands

```bash
python3 diagrams/generate.py          # regenerate derived diagrams (scenario v3 sequences, communication, DB)
python3 export_diagrams.py            # every diagram -> diagrams/out/png + diagrams/out/svg
python3 export_diagrams.py -f png q3  # only PNG, only sources starting with "q3"
python3 export_diagrams.py --check    # syntax check only
python3 verify.py                     # SQL + Java + scenario replay + PlantUML check
uv run --no-project --with python-docx --with pillow python3 build_docx.py        # v5 report + submission_ready/Thiet_ke_3
python3 build_vp.py                   # Visual Paradigm CE must be open with the MCP plugin; builds/exports diagrams/out/vp
uv run --no-project --with python-docx --with pillow python3 build_docx.py --vp   # v5 content with the VP images -> build/
uv run --no-project --with python-docx --with pillow python3 build_full_docx.py   # v8 final report (needs local prompts_appendix.json)
```

Needs Python 3.9+ and Java 17+. Graphviz (`dot`) is used if installed; otherwise PlantUML's built-in Smetana layout is used. On first run, PlantUML 1.2026.8 is downloaded to `~/.cache/plantuml/`, and the test jars (sqlite-jdbc, slf4j, JUnit console, embedded Tomcat 11 + Jasper + ECJ) to `~/.cache/txthanh-verify/`. `--jar` or `$PLANTUML_JAR` selects a different PlantUML jar.

## Verification

`verify.py` does the following:
1. Loads the system schema and sample data in SQLite with foreign keys enforced, and checks that the derived order totals match the scenario tables.
2. Compiles the model, DAO and test classes with `-Xlint:all -Werror`, then runs JUnit:
   - **22 DAO unit tests**, as in the textbook's section 5.3, each on a fresh database;
   - **3 web-flow tests**, which start embedded Tomcat on `java/WebContent` and replay both standard scenarios and their exceptions over HTTP, so every JSP page is compiled and run.
3. Parses all PlantUML sources.
4. Checks that the generated diagrams match their sources.

Current result: **25/25 tests pass, VERIFIED**. Two sanity checks were run by breaking the code on purpose:
- Removing the `status = 'PENDING'` guard from `approveOrder()` made exactly the cancelled-order test fail.
- The web test caught a real bug, fixed before release: the shared JSP include lacked a UTF-8 page encoding, so Vietnamese text in it rendered garbled.


### Audit of the migrated work against question.md

| # | Finding in the cnpm-hrm work | Fix in this folder |
|---|---|---|
| 1 | Q3a/b, Q4a/b and Q5a/b were never done | New: communication diagrams, design class diagrams, DB design, Java code, package and deployment diagrams |
| 2 | Q1b module 1 was a generic step table with no sample data, unlike module 2 | Rewritten as a standard scenario with data (KH01, HD1024…) that matches the module 2 scenario |
| 3 | Q2 only covered module 2, and its diagram title said module 2 only | Entity extraction merged for both modules (module 1 uses a subset of the same 7 classes) |
| 4 | Entity diagram used SaleStaff 1–n Order and DeliveryStaff 1–n Order, but the report says an order may not have a staff member yet | Changed to `0..1 – 0..*`; Order–OrderDetail changed to `1 – 1..*` ("ít nhất một") |
| 5 | Scenario step 12 shows the delivery staff member's area, but `DeliveryStaff` had no `area` attribute | `area` added |
| 6 | `Invoice.status` duplicated `Order.status` (the report says the invoice follows the order) | Removed from Invoice; the invoice status is read from the order |
| 7 | Module 2 use-case diagram had Check Inventory / Update Export Status / Update Inventory, which are internal system steps and not in the report's own list of sub-use-cases | Diagram matches the report's list of 7 sub-use-cases |
| 8 | Overview use-case diagram linked Sale Staff and Customer directly to use cases they already reach through «include», and named them differently from the module diagram | Overview shows each actor's goals once; the detail lives in the module diagrams |
| 9 | State diagram has `ReadyForExport`, which is missing from the report's status table | Redrawn with the 6 statuses of the table; "delivery staff assigned" is a guard on `export()` |
| 10 | Analysis BCE: VP image has `outInvoiceTotal` where the text has `outTotalAmount`; Product was missing `status` | Aligned with the text and the entity class |
| 11 | VP exports carry "evaluation copy" watermarks, and some diagrams existed only as images | All diagrams now have PlantUML sources and clean exports |
| 12 | Step 18 of the module 2 scenario said "cập nhật hóa đơn", which leaves open when the invoice exists | The invoice exists from order placement so the customer can track it; export sets its issue date (`issueInvoice`) |

Items 4–10 and 12 change content that was carried over; the original wording is still in `source/` (untouched docx and markdown).
