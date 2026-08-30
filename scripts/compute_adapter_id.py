"""Compute deterministic adapter_id from canonical JSON source and target.

Usage:
  python scripts/compute_adapter_id.py --source path/to/source.json --target path/to/target.json
  python scripts/compute_adapter_id.py --manifest adapters/<id>/manifest.json

Outputs JSON with adapter_id and hashes.
"""
from __future__ import annotations
import argparse
import json
import hashlib
from typing import Any

ALGORITHM_VERSION = "1.0"


def canonicalize(obj: Any) -> bytes:
    """Return canonical UTF-8 bytes for JSON object: sorted keys, compact separators, LF newlines."""
    def _sorted(o: Any):
        if isinstance(o, dict):
            return {k: _sorted(o[k]) for k in sorted(o.keys())}
        if isinstance(o, list):
            return [_sorted(i) for i in o]
        return o

    sorted_obj = _sorted(obj)
    s = json.dumps(sorted_obj, separators=(",", ":"), ensure_ascii=False)
    # normalize newlines
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return s.encode("utf-8")


def sha256_hex_prefix(data: bytes, length: int = 16) -> str:
    h = hashlib.sha256(data).hexdigest()
    return h[:length]


def compute_adapter_id(source_obj: Any, target_obj: Any) -> dict:
    sbytes = canonicalize(source_obj)
    tbytes = canonicalize(target_obj)
    sh = hashlib.sha256(sbytes).hexdigest()
    th = hashlib.sha256(tbytes).hexdigest()
    adapter_id = f"{sh[:16]}_{th[:16]}"
    return {
        "adapter_id": adapter_id,
        "algorithm_version": ALGORITHM_VERSION,
        "source_hash": sh,
        "target_hash": th,
    }


def load_json_path(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="Path to source JSON")
    parser.add_argument("--target", help="Path to target JSON")
    parser.add_argument("--manifest", help="Path to adapters/<id>/manifest.json that may contain canonical source/target")
    args = parser.parse_args(argv)

    if args.manifest:
        m = load_json_path(args.manifest)
        # Expect manifest to optionally include canonical_source and canonical_target
        if "canonical_source" in m and "canonical_target" in m:
            source_obj = m["canonical_source"]
            target_obj = m["canonical_target"]
        else:
            print("Manifest does not contain canonical_source/canonical_target fields; cannot compute")
            return 3
    else:
        if not (args.source and args.target):
            parser.print_help()
            return 3
        source_obj = load_json_path(args.source)
        target_obj = load_json_path(args.target)

    out = compute_adapter_id(source_obj, target_obj)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
