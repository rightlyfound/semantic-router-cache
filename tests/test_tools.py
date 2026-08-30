from __future__ import annotations

import json
from pathlib import Path

from scripts.compute_adapter_id import adapter_id
from scripts.update_index import build_index

ROOT = Path(__file__).parents[1]


def test_adapter_id_is_key_order_invariant():
    left = {"b": 2, "a": {"y": 1, "x": 0}}
    right = {"a": {"x": 0, "y": 1}, "b": 2}
    assert adapter_id(left, {"target": 1}) == adapter_id(right, {"target": 1})


def test_manifest_id_matches_fingerprints():
    manifest = json.loads((ROOT / "adapters/e18f2f8f95be8660_bb16b0083302ae2a/manifest.json").read_text())
    assert manifest["adapter_id"] == f"{manifest['source_fingerprint']}_{manifest['target_fingerprint']}"


def test_index_matches_manifests():
    expected = build_index(ROOT)
    actual = json.loads((ROOT / "adapters/index.json").read_text())
    assert actual == expected
