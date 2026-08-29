from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path: Path) -> dict:
    return json.loads(path.read_text())

def digest(record: object) -> str:
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

spec = importlib.util.spec_from_file_location("weather_adapter", ROOT / "adapters" / "weather_example.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

source = load_json(ROOT / "fixtures" / "weather_source.json")
target = load_json(ROOT / "fixtures" / "weather_target.json")
adapter_id = f"{digest(source)}_{digest(target)}"
expected = {
    "sunlight_intensity": 0.15,
    "lat": 40.7,
    "lng": -74.0,
    "recorded_at": "2026-08-30T08:17:00+10:00",
}
actual = module.translate(source)
assert actual == expected, (actual, expected)

negative_cases = [
    ({**source, "cloud_density": 101}, ValueError),
    ({**source, "coords": [40.7]}, ValueError),
    ({**source, "timestamp": "not-a-date"}, ValueError),
]
for case, error_type in negative_cases:
    try:
        module.translate(case)
    except error_type:
        pass
    else:
        raise AssertionError(f"expected {error_type.__name__} for {case}")

print(json.dumps({
    "adapter_id": adapter_id,
    "positive_result": actual,
    "negative_cases_passed": len(negative_cases),
    "round_trip": {"status": "not_applicable", "reason": "weather mapping is intentionally lossy and no meaningful reverse mapping was defined"},
    "validation": "passed"
}, sort_keys=True))
