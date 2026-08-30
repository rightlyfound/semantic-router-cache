from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from models.events import PullRequestEvent

ROOT = Path(__file__).parents[1]


def load_adapter(adapter_id: str):
    path = ROOT / "adapters" / adapter_id / "adapter.py"
    spec = importlib.util.spec_from_file_location(adapter_id, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_weather_adapter_happy_path():
    module = load_adapter("e18f2f8f95be8660_bb16b0083302ae2a")
    source = json.loads((ROOT / "fixtures/weather_source.json").read_text())
    result = module.translate(source)
    assert result["sunlight_intensity"] == 0.15
    assert result["lat"] == 40.7
    assert result["lng"] == -74.0


def test_webhook_adapter_matches_target_model():
    module = load_adapter("61381583dec31b83_03e547d1918cb5cf")
    source = json.loads((ROOT / "fixtures/github_pull_request_opened.json").read_text())
    result = module.translate(source)
    validated = PullRequestEvent.model_validate(result)
    assert validated.pr_number == 11049
    assert validated.author_login == "vullgazz"


def test_weather_adapter_rejects_non_object_and_bad_values():
    module = load_adapter("e18f2f8f95be8660_bb16b0083302ae2a")
    with pytest.raises(TypeError):
        module.translate([])
    source = json.loads((ROOT / "fixtures/weather_source.json").read_text())
    source["cloud_density"] = 101
    with pytest.raises(ValueError):
        module.translate(source)
    source = json.loads((ROOT / "fixtures/weather_source.json").read_text())
    source["coords"] = [40.7]
    with pytest.raises(ValueError):
        module.translate(source)
    source = json.loads((ROOT / "fixtures/weather_source.json").read_text())
    source["timestamp"] = "not-a-date"
    with pytest.raises(ValueError):
        module.translate(source)


def test_webhook_adapter_rejects_non_object_and_missing_nested_fields():
    module = load_adapter("61381583dec31b83_03e547d1918cb5cf")
    with pytest.raises(TypeError):
        module.translate([])
    source = json.loads((ROOT / "fixtures/github_pull_request_opened.json").read_text())
    del source["pull_request"]["user"]["login"]
    with pytest.raises(ValueError):
        module.translate(source)


def test_webhook_adapter_rejects_malformed_payload():
    module = load_adapter("61381583dec31b83_03e547d1918cb5cf")
    try:
        module.translate({"action": "edited"})
    except ValueError:
        pass
    else:
        raise AssertionError("malformed payload was accepted")
