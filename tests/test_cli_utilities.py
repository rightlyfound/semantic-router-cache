from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import compute_adapter_id, redaction_check, update_index, validate_manifest

ROOT = Path(__file__).parents[1]


def test_compute_canonical_bytes_and_digest_are_deterministic():
    left = {"z": "é", "a": {"b": 2, "a": 1}}
    right = {"a": {"a": 1, "b": 2}, "z": "é"}
    assert compute_adapter_id.canonical_bytes(left) == compute_adapter_id.canonical_bytes(right)
    assert compute_adapter_id.digest(left) == compute_adapter_id.digest(right)
    assert len(compute_adapter_id.adapter_id(left, right).split("_")) == 2


def test_compute_main_source_target(capsys, monkeypatch, tmp_path):
    source = tmp_path / "source.json"
    target = tmp_path / "target.json"
    source.write_text('{"a": 1}\n')
    target.write_text('{"b": 2}\n')
    monkeypatch.setattr("sys.argv", ["compute_adapter_id.py", "--source", str(source), "--target", str(target)])
    assert compute_adapter_id.main() == 0
    assert len(capsys.readouterr().out.strip().split("_")) == 2


def test_compute_main_requires_target(monkeypatch, tmp_path):
    source = tmp_path / "source.json"
    source.write_text('{"a": 1}\n')
    monkeypatch.setattr("sys.argv", ["compute_adapter_id.py", "--source", str(source)])
    with pytest.raises(SystemExit):
        compute_adapter_id.main()


def test_compute_main_manifest_mode_and_mismatch(capsys, monkeypatch, tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"adapter_id": "a" * 16 + "_" + "b" * 16, "source_fingerprint": "a" * 16, "target_fingerprint": "b" * 16}))
    monkeypatch.setattr("sys.argv", ["compute_adapter_id.py", "--manifest", str(manifest)])
    assert compute_adapter_id.main() == 0
    assert capsys.readouterr().out.strip() == "a" * 16 + "_" + "b" * 16
    manifest.write_text(json.dumps({"adapter_id": "wrong", "source_fingerprint": "a" * 16, "target_fingerprint": "b" * 16}))
    with pytest.raises(SystemExit, match="manifest adapter_id mismatch"):
        compute_adapter_id.main()


def test_redaction_scan_skips_directories_pyc_and_binary(tmp_path):
    directory = tmp_path / "folder"
    directory.mkdir()
    (directory / "ignored.pyc").write_bytes(b"\x00\x01")
    (tmp_path / "binary.dat").write_bytes(b"\xff\xfe")
    assert redaction_check.scan([directory, directory / "ignored.pyc", tmp_path / "binary.dat"]) == []


@pytest.mark.parametrize("text, detector", [
    ("AKIA1234567890ABCDEF", "aws-access-key"),
    ("Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456", "bearer-token"),
    ("ghp_abcdefghijklmnopqrstuvwxyz123456", "github-token"),
    ('api_key = "12345678901234567890"', "generic-secret-assignment"),
])
def test_redaction_scan_detects_high_confidence_patterns(tmp_path, text, detector):
    path = tmp_path / "candidate.txt"
    path.write_text(text)
    findings = redaction_check.scan([path])
    assert any(name == detector for _, _, name in findings)


def test_redaction_main_default_and_explicit_paths(capsys, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "audit").mkdir()
    (tmp_path / "fixtures").mkdir()
    (tmp_path / "audit" / "safe.txt").write_text("safe")
    monkeypatch.setattr("sys.argv", ["redaction_check.py"])
    assert redaction_check.main() == 0
    assert capsys.readouterr().out == ""
    bad = tmp_path / "bad.txt"
    bad.write_text("-----BEGIN PRIVATE KEY-----")
    monkeypatch.setattr("sys.argv", ["redaction_check.py", str(bad)])
    assert redaction_check.main() == 1
    assert "private-key" in capsys.readouterr().out


def test_validate_manifest_cli_valid_and_invalid(capsys, monkeypatch, tmp_path):
    valid = tmp_path / "valid.json"
    valid.write_text((ROOT / "adapters/61381583dec31b83_03e547d1918cb5cf/manifest.json").read_text())
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps({"status": "unknown"}))
    monkeypatch.setattr("sys.argv", ["validate_manifest.py", str(valid), str(invalid)])
    assert validate_manifest.main() == 1
    output = capsys.readouterr().out
    assert '"valid": true' in output
    assert '"valid": false' in output
    monkeypatch.setattr("sys.argv", ["validate_manifest.py", str(valid)])
    assert validate_manifest.main() == 0
    assert '"valid": true' in capsys.readouterr().out


def write_adapter(root: Path, name: str = "abc") -> Path:
    directory = root / "adapters" / name
    directory.mkdir(parents=True)
    (directory / "adapter.py").write_text("def translate(data):\n    return data\n")
    (directory / "manifest.json").write_text(json.dumps({"adapter_id": name, "created_at": "2026-01-01T00:00:00Z", "status": "valid"}))
    return directory


def test_update_index_builds_and_writes_atomically(tmp_path, capsys, monkeypatch):
    write_adapter(tmp_path)
    monkeypatch.setattr("sys.argv", ["update_index.py", "--root", str(tmp_path)])
    assert update_index.main() == 0
    index = json.loads((tmp_path / "adapters" / "index.json").read_text())
    assert index["adapters"][0]["adapter_id"] == "abc"
    assert str(tmp_path / "adapters" / "index.json") in capsys.readouterr().out
    monkeypatch.setattr("sys.argv", ["update_index.py", "--root", str(tmp_path), "--check"])
    assert update_index.main() == 0
    assert "current" in capsys.readouterr().out


def test_update_index_check_detects_missing_or_stale_index(tmp_path, capsys, monkeypatch):
    write_adapter(tmp_path)
    monkeypatch.setattr("sys.argv", ["update_index.py", "--root", str(tmp_path), "--check"])
    assert update_index.main() == 1
    assert "stale or missing" in capsys.readouterr().out


def test_update_index_rejects_mismatch_and_missing_adapter(tmp_path):
    directory = write_adapter(tmp_path, "abc")
    (directory / "manifest.json").write_text(json.dumps({"adapter_id": "different"}))
    with pytest.raises(ValueError, match="directory/manifest mismatch"):
        update_index.build_index(tmp_path)
    (directory / "manifest.json").write_text(json.dumps({"adapter_id": "abc"}))
    (directory / "adapter.py").unlink()
    with pytest.raises(ValueError, match="missing adapter.py"):
        update_index.build_index(tmp_path)


def test_update_index_empty_repository(tmp_path):
    result = update_index.build_index(tmp_path)
    assert result["adapters"] == []
