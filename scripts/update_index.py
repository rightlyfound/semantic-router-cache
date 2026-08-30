#!/usr/bin/env python3
"""Build or verify the derived adapter index."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


def build_index(root: Path) -> dict:
    entries = []
    seen = set()
    for manifest_path in sorted((root / "adapters").glob("*/manifest.json")):
        adapter_dir = manifest_path.parent
        adapter_id = adapter_dir.name
        if adapter_id in seen:
            raise ValueError(f"duplicate adapter_id: {adapter_id}")
        seen.add(adapter_id)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("adapter_id") != adapter_id:
            raise ValueError(f"directory/manifest mismatch: {adapter_id}")
        if not (adapter_dir / "adapter.py").is_file():
            raise ValueError(f"missing adapter.py: {adapter_id}")
        entries.append({
            "adapter_id": adapter_id,
            "created_at": manifest.get("created_at"),
            "source_fingerprint": manifest.get("source_fingerprint"),
            "target_fingerprint": manifest.get("target_fingerprint"),
            "status": manifest.get("status"),
            "path": f"adapters/{adapter_id}",
        })
    return {"generated": True, "index_version": "1", "adapters": entries}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    expected = build_index(root)
    output = root / "adapters" / "index.json"
    actual = json.loads(output.read_text(encoding="utf-8")) if output.exists() else None
    if args.check:
        if actual != expected:
            print("adapter index is stale or missing")
            return 1
        print("adapter index is current")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="index-", dir=output.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(expected, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temp_name, output)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
