# Contributing to semantic-router-cache

All adapter changes require a human-reviewed pull request. Agent-generated code is treated as untrusted until it passes the manifest validator, isolated tests, redaction checks, and target-contract validation.

## Add an adapter

Create `adapters/{adapter_id}/adapter.py` and `adapters/{adapter_id}/manifest.json`. Store canonical source and target records in `schemas/`, safe minimal fixtures in `fixtures/`, and a redacted provenance record in `audit/`. Compute the ID with:

```bash
python scripts/compute_adapter_id.py --source schemas/source.json --target schemas/target.json
```

Validate the manifest and repository before requesting review:

```bash
python scripts/validate_manifest.py adapters/{adapter_id}/manifest.json
python scripts/update_index.py --check --root .
python scripts/redaction_check.py audit fixtures
pytest -q
```

## Review checklist

Reviewers should confirm that the source and target contracts are explicit, the mapping handles missing and malformed values, lossiness is documented, dependencies are recorded, fixtures are safe, and no generated code performs network access, filesystem writes, subprocess execution, credential access, or production writes.

Preview mode must not commit. Promotion is permitted only after the validation result is reproducible and the intended files are understood. Do not create schedules, open external issues, or send messages as an incidental effect of a code change.

## Schema evolution

Manifest changes require a `schema_version` update when compatibility is affected. Compatible additions should preserve existing readers; breaking changes require a migration note and validation of every valid adapter. Mark affected adapters `stale` rather than silently reusing them. Deprecated or superseded records retain their audit history and move to the archive according to the Semantic OS policy.

## Branches and commits

Use `feat/`, `fix/`, `chore/`, `docs/`, `test/`, or `ci/` prefixes. Keep each pull request focused and use one logical commit where practical. Never include credentials, raw sensitive payloads, private keys, or unredacted audit data.
