"""Generate adapters/index.json from adapters/*/manifest.json (derived index).

Usage:
  python scripts/update_index.py --out adapters/index.json
  python scripts/update_index.py --check

The script validates manifests (using the Pydantic model) and fails on duplicates.
"""
from __future__ import annotations
import argparse
import json
import os
from datetime import datetime
from typing import List, Dict

from models.adapter_manifest import validate_manifest

ALGORITHM_VERSION = "1.0"


def find_manifests(root: str) -> List[str]:
    manifests = []
    for name in os.listdir(root):
        p = os.path.join(root, name)
        if os.path.isdir(p):
            m = os.path.join(p, "manifest.json")
            if os.path.isfile(m):
                manifests.append(m)
    return manifests


def load_manifest(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_index(root: str) -> Dict:
    entries = []
    seen = set()
    errors = []
    for mpath in find_manifests(root):
        ok, errs = validate_manifest(mpath)
        rel = os.path.relpath(mpath)
        if not ok:
            errors.append({"file": rel, "errors": errs})
            # skip invalid
            continue
        manifest = load_manifest(mpath)
        aid = manifest.get("adapter_id")
        if aid in seen:
            raise SystemExit(f"Duplicate adapter_id detected: {aid} (file: {mpath})")
        seen.add(aid)
        entries.append({
            "adapter_id": aid,
            "path": os.path.dirname(os.path.relpath(mpath)),
            "created_at": manifest.get("created_at"),
            "source_fingerprint": manifest.get("source_fingerprint"),
            "target_fingerprint": manifest.get("target_fingerprint"),
            "status": manifest.get("status"),
        })
    index = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "algorithm_version": ALGORITHM_VERSION,
        "adapters": sorted(entries, key=lambda e: e["adapter_id"]),
    }
    return index, errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="adapters", help="Adapters root dir")
    parser.add_argument("--out", help="Path to write adapters/index.json")
    parser.add_argument("--check", action="store_true", help="Check against existing index and report drift")
    args = parser.parse_args(argv)

    index, errors = build_index(args.root)
    if args.check:
        existing = None
        outpath = os.path.join(args.root, "index.json")
        if os.path.exists(outpath):
            with open(outpath, "r", encoding="utf-8") as f:
                existing = json.load(f)
        if existing is None:
            print("No existing index.json found; consider generating one")
            # treat as drift
            return 2
        if existing.get("adapters") != index.get("adapters"):
            print("Index drift detected")
            # show simple diff summary
            ex_set = {e['adapter_id'] for e in existing.get('adapters', [])}
            new_set = {e['adapter_id'] for e in index.get('adapters', [])}
            added = new_set - ex_set
            removed = ex_set - new_set
            print({"added": sorted(list(added)), "removed": sorted(list(removed))})
            return 2
        print("Index up-to-date")
        return 0

    if args.out:
        outdir = os.path.dirname(args.out)
        if outdir and not os.path.exists(outdir):
            os.makedirs(outdir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)
        print(f"Wrote index to {args.out}")
        if errors:
            print("Some manifests failed validation:")
            print(json.dumps(errors, indent=2))
            return 2
        return 0

    print(json.dumps(index, indent=2))
    if errors:
        print(json.dumps(errors, indent=2))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
