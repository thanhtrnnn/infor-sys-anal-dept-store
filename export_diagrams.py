#!/usr/bin/env python3
"""Export the PlantUML diagrams in diagrams/src/ to PNG and/or SVG.

Usage (from any directory):
    python3 export_diagrams.py                 # PNG + SVG for every diagram
    python3 export_diagrams.py -f png          # PNG only
    python3 export_diagrams.py q3a q5b         # only sources whose name starts with q3a / q5b
    python3 export_diagrams.py --check         # syntax check only, writes nothing

PlantUML is looked up in this order: --jar, $PLANTUML_JAR, the cached jar in
~/.cache/plantuml/, then downloaded from the official GitHub release (pinned
version below). Java 11+ is required; Graphviz `dot` is used when installed,
otherwise PlantUML's built-in Smetana layout engine is used.
Sources whose name starts with "_" are include files and are not exported.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "diagrams" / "src"
OUT = ROOT / "diagrams" / "out"
VERSION = "1.2026.8"
URL = f"https://github.com/plantuml/plantuml/releases/download/v{VERSION}/plantuml-{VERSION}.jar"
CACHE = Path.home() / ".cache" / "plantuml" / f"plantuml-{VERSION}.jar"


def plantuml_jar(explicit: str | None) -> Path:
    for candidate in (explicit, os.environ.get("PLANTUML_JAR")):
        if candidate:
            jar = Path(candidate).expanduser()
            if not jar.is_file():
                sys.exit(f"PlantUML jar not found: {jar}")
            return jar
    if not CACHE.is_file():
        print(f"Downloading PlantUML {VERSION} -> {CACHE}")
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        tmp = CACHE.with_suffix(".part")
        urllib.request.urlretrieve(URL, tmp)
        tmp.replace(CACHE)
    return CACHE


def sources(prefixes: list[str]) -> list[Path]:
    files = sorted(p for p in SRC.glob("*.puml") if not p.name.startswith("_"))
    if prefixes:
        files = [p for p in files if any(p.name.startswith(x) for x in prefixes)]
    return files


def run(jar: Path, args: list[str], files: list[Path]) -> subprocess.CompletedProcess:
    java = shutil.which("java") or sys.exit("java not found on PATH")
    cmd = [java, "-Djava.awt.headless=true", "-DPLANTUML_LIMIT_SIZE=16384", "-jar", str(jar), "-charset", "UTF-8"]
    if not shutil.which("dot"):
        cmd.append("-Playout=smetana")
    return subprocess.run(cmd + args + [str(f) for f in files], text=True, capture_output=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("only", nargs="*", help="export only sources whose file name starts with one of these")
    ap.add_argument("-f", "--format", choices=("png", "svg", "all"), default="all")
    ap.add_argument("--jar", help="path to plantuml.jar")
    ap.add_argument("--check", action="store_true", help="check syntax only, write nothing")
    a = ap.parse_args()

    files = sources(a.only)
    if not files:
        print(f"no diagram sources matched in {SRC}", file=sys.stderr)
        return 2
    jar = plantuml_jar(a.jar)

    if a.check:
        r = run(jar, ["-checkonly", "-failfast2"], files)
        print(r.stdout + r.stderr or f"{len(files)} sources OK")
        return r.returncode

    failed = False
    for fmt in (("png", "svg") if a.format == "all" else (a.format,)):
        out = OUT / fmt
        out.mkdir(parents=True, exist_ok=True)
        r = run(jar, [f"-t{fmt}", "-o", str(out)], files)
        if r.returncode:
            failed = True
            print(r.stdout + r.stderr, file=sys.stderr)
        for f in files:
            target = out / f"{f.stem}.{fmt}"
            ok = target.is_file() and target.stat().st_mtime >= f.stat().st_mtime
            failed |= not ok
            print(f"{'OK ' if ok else 'ERR'} {target.relative_to(ROOT)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
