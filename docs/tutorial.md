# Add an adapter tutorial

Start with a safe source fixture and an authoritative target model. Record both as canonical JSON under `schemas/`, then compute the identity:

```bash
python scripts/compute_adapter_id.py --source schemas/source.json --target schemas/target.json
```

Create the adapter directory and add `adapter.py`, `manifest.json`, safe fixtures, tests, and a redacted audit record. Keep the adapter pure and deterministic unless an explicitly reviewed integration requires otherwise.

Run the local gates:

```bash
python scripts/validate_manifest.py adapters/{adapter_id}/manifest.json
python scripts/update_index.py --root .
python scripts/redaction_check.py audit fixtures
pytest -q
```

Inspect the diff and ask a human reviewer to confirm the mapping, dependencies, optional-field behavior, type coercions, timezone policy, and lossiness. Use preview mode until that review is complete. A passing happy path is insufficient; include malformed input, missing required fields, missing optional fields, wrong types, and boundary cases relevant to the contract.

The weather and webhook adapters in this repository are examples only. They do not establish production latency, continuous availability, zero-loss delivery, or authorization to send data to external systems.
