#!/usr/bin/env python3
"""Compute a deterministic Semantic OS adapter ID from canonical JSON records."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CANONICALIZATION_VERSION = "1"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()[:16]


def adapter_id(source: Any, target: Any) -> str:
    return f"{digest(source)}_{digest(target)}"


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source", type=Path)
    group.add_argument("--manifest", type=Path)
    parser.add_argument("--target", type=Path)
    args = parser.parse_args()
    if args.source:
        if args.target is None:
            parser.error("--target is required with --source")
        source = json.loads(args.source.read_text(encoding="utf-8"))
        target = json.loads(args.target.read_text(encoding="utf-8"))
    else:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        computed = f"{manifest['source_fingerprint']}_{manifest['target_fingerprint']}"
        if manifest.get("adapter_id") != computed:
            raise SystemExit(f"manifest adapter_id mismatch: expected {computed}")
        print(computed)
        return 0
    print(adapter_id(source, target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
