"""Tests for compute_adapter_id invariance and update_index behavior."""
from __future__ import annotations
import json
import tempfile
import os
from scripts.compute_adapter_id import compute_adapter_id, canonicalize
from scripts.update_index import build_index


def test_canonicalization_ordering():
    a = {"b": 1, "a": 2}
    b = {"a": 2, "b": 1}
    assert canonicalize(a) == canonicalize(b)


def test_compute_adapter_id_deterministic(tmp_path):
    s = {"x": [1,2,3], "a": {"z": 1}}
    t = {"y": 2}
    out1 = compute_adapter_id(s, t)
    out2 = compute_adapter_id(s, t)
    assert out1['adapter_id'] == out2['adapter_id']

# Note: build_index expects a directory with adapter dirs; create a minimal example

def test_update_index(tmp_path):
    root = tmp_path / "adapters"
    root.mkdir()
    # create one adapter dir
    ad = root / "abcdabcdabcdabcd_efefefefefefefef"
    ad.mkdir()
    manifest = {
        "schema_version": "2026-08-1",
        "adapter_id": "abcdabcdabcdabcd_efefefefefefefef",
        "created_at": "2026-08-30T12:00:00Z",
        "source_fingerprint": "s",
        "target_fingerprint": "t",
        "mapping_policy": {},
        "dependency_versions": {},
        "validation_authority": "team",
        "models_used": [],
        "synthesis_mode": "single_pass",
        "context_references": [],
        "fixture_ids": [],
        "test_result": "passed",
        "lossiness": [],
        "redactions": [],
        "status": "proposed"
    }
    with open(ad / 'manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f)
    # monkeypatch model validation by relying on scripts.update_index build_index which calls validate_manifest
    # For simplicity, just ensure build_index runs without exception
    index, errors = build_index(str(root))
    assert 'adapters' in index
