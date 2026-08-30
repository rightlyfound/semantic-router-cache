#!/usr/bin/env python3
"""Validate one or more adapter manifests without executing adapters."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.adapter_manifest import validate_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    failures = 0
    for path in args.paths:
        valid, errors = validate_manifest(path)
        if valid:
            print(json.dumps({"path": str(path), "valid": True}, sort_keys=True))
        else:
            failures += 1
            print(json.dumps({"path": str(path), "valid": False, "errors": errors}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
