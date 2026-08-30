#!/usr/bin/env python3
"""Scan selected files for high-confidence credential patterns."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

PATTERNS = [
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("bearer-token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}", re.IGNORECASE)),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("generic-secret-assignment", re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{16,}['\"]")),
]


def scan(paths: list[Path]) -> list[tuple[Path, int, str]]:
    findings = []
    for path in paths:
        if not path.is_file() or path.suffix in {".pyc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for name, pattern in PATTERNS:
                if pattern.search(line):
                    findings.append((path, line_no, name))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()
    paths = args.paths or [Path("audit"), Path("fixtures")]
    expanded = [item for path in paths for item in (path.rglob("*") if path.is_dir() else [path])]
    findings = scan(expanded)
    for path, line_no, name in findings:
        print(f"{path}:{line_no}: {name} detector matched; review and redact without printing the value")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
