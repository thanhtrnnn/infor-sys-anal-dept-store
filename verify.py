#!/usr/bin/env python3
"""Verify the TXTHANH answer end to end.

1. SQL    – builds sql/system_schema.sql + sql/system_sample_data.sql in SQLite with foreign keys on, checks FK integrity
            and that the derived order totals match the scenario tables.
2. Java   – compiles java/src (model + dao, Q4b) and java/test with -Xlint:all -Werror, then runs JUnit:
            * unittest.*  – one test class per DAO, a fresh database per test (textbook 5.3: "rollback after each test");
            * webtest.*   – starts embedded Tomcat on java/WebContent and replays both standard scenarios and their
                            exceptions over HTTP, so every JSP page is compiled and executed.
3. UML    – syntax-checks every PlantUML source (export_diagrams.py --check).
4. Derived diagrams (diagrams/generate.py) are up to date with scenario v2/v3 and system_schema.sql.

Jars (sqlite-jdbc, slf4j, JUnit console, embedded Tomcat + Jasper + ECJ) are downloaded once from Maven Central into
~/.cache/txthanh-verify. Requires Java 17+.
"""
from __future__ import annotations

import shutil
import sqlite3
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JAVA = ROOT / "java"
CACHE = Path.home() / ".cache" / "txthanh-verify"
MAVEN = "https://repo1.maven.org/maven2"
TOMCAT = "11.0.26"
JARS = {
    "sqlite-jdbc-3.53.4.0.jar": "org/xerial/sqlite-jdbc/3.53.4.0",
    "slf4j-api-2.0.17.jar": "org/slf4j/slf4j-api/2.0.17",
    "junit-platform-console-standalone-6.1.3.jar": "org/junit/platform/junit-platform-console-standalone/6.1.3",
    f"tomcat-embed-core-{TOMCAT}.jar": f"org/apache/tomcat/embed/tomcat-embed-core/{TOMCAT}",
    f"tomcat-embed-jasper-{TOMCAT}.jar": f"org/apache/tomcat/embed/tomcat-embed-jasper/{TOMCAT}",
    f"tomcat-embed-el-{TOMCAT}.jar": f"org/apache/tomcat/embed/tomcat-embed-el/{TOMCAT}",
    f"tomcat-annotations-api-{TOMCAT}.jar": f"org/apache/tomcat/tomcat-annotations-api/{TOMCAT}",
    "ecj-3.46.100.jar": "org/eclipse/jdt/ecj/3.46.100",
}


def jar(name: str) -> Path:
    path = CACHE / name
    if not path.is_file():
        CACHE.mkdir(parents=True, exist_ok=True)
        print(f"   downloading {name}")
        urllib.request.urlretrieve(f"{MAVEN}/{JARS[name]}/{name}", path)
    return path


def check_sql() -> None:
    print("1. System DB (Q4a): schema + sample data (SQLite, foreign_keys=ON)")
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    for f in ("system_schema.sql", "system_sample_data.sql"):
        con.executescript((ROOT / "sql" / f).read_text(encoding="utf-8"))
    assert not con.execute("PRAGMA foreign_key_check").fetchall(), "foreign key violations"
    totals = dict(con.execute("""SELECT o.code, SUM(d.quantity * d.unitPrice) FROM tblOrder o
                                 JOIN tblOrderDetail d ON d.tblOrderid = o.id GROUP BY o.id"""))
    expected = {"DH1024": 1_250_000, "DH1025": 320_000, "DH1026": 780_000, "DH0987": 540_000, "DH1011": 175_000}
    assert all(totals[k] == v for k, v in expected.items()), totals
    tables = con.execute("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'").fetchone()[0]
    print(f"   ok: {tables} tables, FK clean, derived totals match the scenarios (DH1024 = 1.250.000)")


def check_java(build: Path) -> None:
    print("2. Java (Q4b): compile + JUnit (DAO unit tests + JSP web flow in embedded Tomcat)")
    javac, java = shutil.which("javac"), shutil.which("java")
    if not (javac and java):
        sys.exit("javac/java not found")
    libs = [jar(n) for n in JARS]
    cp = ":".join(str(p) for p in libs)
    sources = sorted(str(p) for d in ("src", "test") for p in (JAVA / d).rglob("*.java"))
    r = subprocess.run([javac, "-encoding", "UTF-8", "--release", "17", "-Xlint:all", "-Werror", "-d", str(build),
                        "-cp", cp, *sources], text=True, capture_output=True)
    if r.returncode:
        sys.exit(f"javac failed:\n{r.stdout}{r.stderr}")
    print(f"   ok: {len(sources)} source files compiled with -Xlint:all -Werror")
    r = subprocess.run([java, "--enable-native-access=ALL-UNNAMED", "-Dslf4j.internal.verbosity=ERROR",
                        f"-Ddeptstore.sql.dir={ROOT / 'sql'}", f"-Ddeptstore.webcontent={JAVA / 'WebContent'}",
                        "-jar", str(jar("junit-platform-console-standalone-6.1.3.jar")), "execute",
                        "--class-path", f"{build}:{cp}", "--scan-class-path", "--disable-banner",
                        "--details=tree", "--disable-ansi-colors"],
                       text=True, capture_output=True, cwd=JAVA)
    report = r.stdout.strip().splitlines()
    tree = [l for l in report if any(t in l for t in ("✔", "✘", "↷"))]
    print("   " + "\n   ".join(tree))
    summary = [l.strip() for l in report if "tests successful" in l or "tests failed" in l]
    print("   " + " | ".join(summary))
    if r.returncode:
        sys.exit(f"JUnit failed:\n{r.stdout[-6000:]}\n{r.stderr[-6000:]}")


def check_uml() -> None:
    print("3. PlantUML syntax")
    r = subprocess.run([sys.executable, str(ROOT / "export_diagrams.py"), "--check"], text=True, capture_output=True)
    n = sum(1 for p in (ROOT / "diagrams" / "src").glob("*.puml") if not p.name.startswith("_"))
    if r.returncode:
        sys.exit(f"PlantUML check failed:\n{r.stdout}{r.stderr}")
    print(f"   ok: {n} diagram sources parse")


def check_generated() -> None:
    print("4. Generated diagrams")
    src = ROOT / "diagrams" / "src"
    derived = ["q3c-3-sequence-design-track-invoice.puml", "q3c-4-sequence-design-approve-export.puml",
               "q3a-3-communication-track-invoice.puml", "q3a-4-communication-approve-export.puml",
               "q4a-database-system.puml", "q4a-2-database-two-modules.puml"]
    before = {f: (src / f).read_text(encoding="utf-8") for f in derived}
    r = subprocess.run([sys.executable, str(ROOT / "diagrams" / "generate.py")], text=True, capture_output=True)
    if r.returncode:
        sys.exit(f"generate.py failed:\n{r.stdout}{r.stderr}")
    stale = [f for f in derived if (src / f).read_text(encoding="utf-8") != before[f]]
    if stale:
        sys.exit(f"generated diagrams were stale (now regenerated, re-export them): {stale}")
    print(f"   ok: {len(derived)} generated diagrams match scenario v2/v3 and system_schema.sql")


def main() -> None:
    check_sql()
    with tempfile.TemporaryDirectory() as tmp:
        check_java(Path(tmp) / "classes")
    check_uml()
    check_generated()
    print("VERIFIED")


if __name__ == "__main__":
    main()
