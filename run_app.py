#!/usr/bin/env python3
"""Run the department store web app locally (embedded Tomcat + SQLite sample data), no MySQL/Tomcat install needed.

    python3 run_app.py            # http://localhost:8080/gdLogin.jsp
    python3 run_app.py --port 9090

Accounts from sql/system_sample_data.sql: customer an/123456, sale staff lan/123456.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from verify import JARS, JAVA, ROOT, jar


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    port = ap.parse_args().port
    javac, java = shutil.which("javac"), shutil.which("java")
    if not (javac and java):
        sys.exit("javac/java not found (Java 17+ required)")
    cp = ":".join(str(jar(n)) for n in JARS)
    build = Path(tempfile.mkdtemp(prefix="deptstore-classes"))
    sources = sorted(str(p) for d in ("src", "test") for p in (JAVA / d).rglob("*.java"))
    subprocess.run([javac, "-encoding", "UTF-8", "--release", "17", "-d", str(build), "-cp", cp, *sources], check=True)
    subprocess.run([java, "--enable-native-access=ALL-UNNAMED", "-Dslf4j.internal.verbosity=ERROR",
                    f"-Ddeptstore.sql.dir={ROOT / 'sql'}", f"-Ddeptstore.webcontent={JAVA / 'WebContent'}",
                    f"-Ddeptstore.port={port}", "-cp", f"{build}:{cp}", "run.DevServer"], cwd=JAVA)


if __name__ == "__main__":
    main()
