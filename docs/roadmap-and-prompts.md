# Semantic OS: Reliability Roadmap and Prompt Pack

This document turns the proposed TODO list into a staged engineering plan for the `semantic-router-cache` repository. It is intentionally conservative: the repository is a reviewed source of truth and audit surface, while Manus schedules and deployed services remain separate execution layers.

## Design decisions applied

The project should optimize for **correctness before scale**, **deterministic reuse before repeated synthesis**, and **human-reviewable changes before autonomous writes**. Generated adapters are untrusted until they pass static inspection, isolated tests, target-contract validation, redaction checks, and provenance review. No prompt should claim zero negotiation, zero packet loss, production readiness, historical novelty, or fixed latency unless those properties have been measured and independently demonstrated.

The repository should have one canonical manifest schema, one canonical adapter layout, one consolidated CI workflow, and one generated adapter index. The index is a derived convenience view, not a second source of truth. The Manus maintenance schedule is the control plane for periodic checks; GitHub Actions may validate pull requests but must not silently mutate the repository or regenerate adapters.

## Prioritized rollout

| Phase | Timing | Deliverable | Exit gate |
|---|---:|---|---|
| 0 | Now | Clean repository hygiene, dependency index, schema version policy, and prompt corrections | No ambiguous source of truth; working tree and generated artifacts reviewed |
| 1 | Next few days | Manifest JSON Schema, Pydantic model, validator CLI, and tests | Existing valid manifests pass; negative fixtures fail clearly |
| 2 | Week 1 | Adapter layout migration, deterministic ID utility, derived index, and adapter tests | Weather and webhook adapters pass from canonical locations |
| 3 | Week 2 | One consolidated CI workflow with lint, schema validation, tests, and redaction scan | Pull requests fail safely and reproducibly on invalid artifacts |
| 4 | Week 2–3 | Governance docs, contributor tutorial, deprecation policy, and schedule manifests | A new contributor can add an adapter without undocumented knowledge |
| 5 | After first maintenance cycle | JSONPlaceholder or another low-risk API bridge in preview mode | Lossiness, optional fields, dependency requirements, and cache reuse are demonstrated |
| 6 | Later | Runtime/API bridge or code-port experiments | Buffering, rollback, approval, observability, and deployment boundaries are designed first |

Do not start Phase 5 or Phase 6 until the first combined maintenance run has produced an auditable result. Do not describe the system as a production runtime until a separately deployed execution service has measurable delivery, latency, concurrency, rollback, and security properties.

## Prompt 0 — Repository assessment and hygiene

```text
Goal:
Assess the semantic-router-cache repository without changing behavior. Produce a proposed diff only.

Read:
- skills/SEMANTIC_OS.md
- README.md
- all adapter manifests and adapter implementations
- schemas/ and audit/ README files

Check:
1. Identify the canonical adapter layout and every exception.
2. Identify duplicate or conflicting sources of truth.
3. Identify untracked generated artifacts, Python cache files, raw payloads, or secrets.
4. Check whether schemas/dependency_index.json exists and list the dependencies actually used by valid adapters.
5. Check whether each manifest has a schema version, synthesis mode, validation authority, fixture IDs, and status.
6. Do not infer production readiness, zero-loss behavior, fixed latency, or autonomous side effects from repository contents.

Return:
- discovered facts;
- risks and inconsistencies;
- a minimal ordered remediation plan;
- no writes, commits, schedules, external messages, or adapter regeneration.
```

## Prompt 1 — Manifest contract and validator

```text
Goal:
Create one machine-enforced adapter manifest contract and validator. Work on a branch and show the diff before any push or merge.

Files:
- schemas/adapter_manifest.schema.json
- models/adapter_manifest.py
- scripts/validate_manifest.py
- tests/test_manifest_validation.py
- requirements-dev.txt only if missing

Requirements:
1. Use JSON Schema Draft 2020-12 and Pydantic v2 with matching field names and semantics.
2. Include schema_version, adapter_id, created_at, source_fingerprint, target_fingerprint, mapping_policy, dependency_versions, validation_authority, models_used, synthesis_mode, context_references, fixture_ids, test_result, lossiness, redactions, status, and optional generator metadata.
3. Set synthesis_mode enum to single_pass, two_pass, and repair_attempt. Do not use an obsolete or ambiguous enum.
4. Use strict types where practical. Permit structured metadata through explicitly named extension fields rather than requiring all additional values to be non-empty strings.
5. Require adapter_id to match the documented fingerprint format or an explicitly documented stable example ID.
6. Validate RFC3339 timestamps, non-empty identifiers, and safe relative fixture paths.
7. Provide validate_manifest(path_or_dict) -> (bool, errors) and a CLI with deterministic exit codes and structured errors.
8. Test one valid weather or webhook manifest and at least three invalid cases: missing required field, wrong type, and invalid enum/status.
9. Do not modify adapters, audit records, fixtures, schedules, or GitHub settings.
10. Do not execute generated adapters during schema validation.

Acceptance:
- JSON Schema and Pydantic validation agree on all fixtures.
- CLI and pytest pass locally.
- No secrets or raw sensitive payloads are introduced.
```

## Prompt 2 — Canonical IDs, adapter layout, and index

```text
Goal:
Make adapter identity and discovery deterministic without changing adapter behavior.

Tasks:
1. Implement scripts/compute_adapter_id.py using canonical JSON: recursive key ordering, UTF-8 encoding, normalized LF line endings, no insignificant whitespace, and explicit versioning of the canonicalization algorithm.
2. Do not perform best-effort semantic rewriting of datetime-like strings; canonicalize declared records, not arbitrary values.
3. Implement scripts/update_index.py to derive adapters/index.json from valid adapter directories and manifests. Write atomically and fail on duplicate IDs, missing manifests, path traversal, or fingerprint mismatch.
4. Migrate flat adapters into adapters/{adapter_id}/adapter.py and manifest.json only after verifying their existing IDs and validation history. Preserve history and keep a migration note.
5. Add tests for key-order invariance, newline invariance, duplicate detection, stale status, and index regeneration.
6. Add a read-only `--check` mode for CI; it must report drift without rewriting files.

Acceptance:
- The same canonical records always produce the same ID.
- The index is reproducible and clearly marked as derived.
- Existing weather and webhook adapters still pass their safe fixtures.
```

## Prompt 3 — Consolidated CI and redaction checks

```text
Goal:
Create one minimal, reproducible GitHub Actions workflow for pull requests and pushes to main.

Tasks:
1. Add .github/workflows/ci.yml; do not create overlapping manifest-specific workflows.
2. Pin the Python major/minor version and install dependencies from a reviewed requirements-dev.txt with an explicit lock or bounded versions where practical.
3. Run, in order: syntax checks, manifest validation, index --check, redaction scan, lint, and pytest.
4. Run in a least-privilege environment. CI must not have repository write permissions, cloud credentials, or production network access.
5. Add scripts/redaction_check.py with conservative detectors for private-key headers, common cloud-token formats, bearer tokens, and high-entropy candidates. Treat emails and realistic fixture values as review signals, not automatic secrets, unless a policy explicitly says otherwise.
6. Make the scanner operate on the diff when available and on audit/fixtures as a fallback. Print file, line, detector, and remediation guidance without echoing the suspected secret.
7. Include synthetic tests and a documented false-positive review path.

Acceptance:
- CI is deterministic, fails closed for high-confidence secret patterns, and does not mutate the repository.
- The workflow does not run adapters against production payloads.
```

## Prompt 4 — Governance and contributor experience

```text
Goal:
Document safe contribution and schema evolution practices without making an unapproved licensing decision.

Files:
- CONTRIBUTING.md
- docs/tutorial.md
- docs/SCHEMA_EVOLUTION.md
- .github/pull_request_template.md
- audit/README.md if needed

Requirements:
1. Explain the canonical adapter layout, manifest schema, fixture rules, validation commands, branch naming, and human review requirement.
2. Define status transitions: proposed -> valid; valid -> stale; stale -> valid only after revalidation; invalid and deprecated require explicit review.
3. Define manifest schema_version migration policy, backward compatibility, deprecation, replacement references, and retention of audit history.
4. Explain that generated code is review-required and that preview mode never commits.
5. Explain redaction policy and the distinction between safe synthetic fixtures and real payloads.
6. Do not add a LICENSE until the repository owner chooses a license. If requested, create a separate license decision change.
7. Do not require agents to create branches, push, or open pull requests unless the user explicitly authorizes that operation.

Acceptance:
- A contributor can add a small deterministic adapter by following the tutorial.
- Governance docs do not claim capabilities that the repository or runtime does not provide.
```

## Prompt 5 — Safe API bridge demonstration

```text
Goal:
Test a low-risk nested API-to-Pydantic bridge in preview and validate mode before any commit.

Source:
JSONPlaceholder user object, preferably pasted or retrieved from its public endpoint only when the user explicitly requests retrieval.

Target:
models/user_profile.py with UserProfile fields user_id, full_name, email, city, latitude, longitude, company_name, and phone_primary.

Required handling:
- address.city -> city;
- address.geo.lat/lng strings -> floats;
- company.name -> company_name;
- phone primary number -> phone_primary, with extension lossiness documented;
- body-independent optional/missing nested sections must produce explicit validation errors or documented defaults;
- EmailStr validation must declare and install the required email-validation dependency.

Tests:
1. Valid fixture.
2. Missing geo.
3. Missing company.
4. Malformed email.
5. Phone without extension and phone with extension.

Safety:
- Use a bounded, public, non-sensitive fixture.
- Do not claim sub-second performance; measure locally if latency matters.
- Do not commit until the user reviews the proposed adapter, assumptions, dependency changes, lossiness, and tests.
- Do not call third-party write endpoints.
```

## Prompt 6 — Runtime/API bridge readiness review

```text
Goal:
Review whether an adapter is ready to move from repository validation into a deployed runtime. Do not deploy.

Assess:
- input authentication and authorization boundaries;
- buffering and backpressure during synthesis;
- atomic activation and rollback of a new adapter version;
- duplicate delivery and idempotency;
- timeout, retry, and circuit-breaker policy;
- observability for cache hits, synthesis calls, validation failures, latency, dropped fields, and stale transitions;
- data retention and redaction;
- concurrency and multi-tenant isolation;
- human approval for schema-changing or externally visible writes.

Return a readiness gap report. A passing repository test is not evidence of zero packet loss, continuous availability, or production readiness.
```

## Long-term maintenance rules

Every quarter, review the manifest schema, dependency index, CI runtime, redaction false-positive rate, adapter reuse rate, stale-adapter count, and audit retention. Every year, review dependency support windows, Python compatibility, cryptographic/hash policy, repository access controls, schedule behavior, and whether the cache should remain in GitHub or move metadata to a database while retaining Git history.

Keep derived files reproducible. Prefer a single consolidated CI workflow and one combined maintenance schedule. Use Manus schedules for controlled periodic checks and GitHub Actions for validation, not for unsupervised regeneration or production writes. Treat model names, output limits, connector availability, and documentation locations as live facts that must be rechecked at execution time.

## Definition of done for future adapters

An adapter is not complete merely because its happy path works. It must have a deterministic identity, a valid manifest, isolated fixtures, positive and negative tests, explicit optional/null/type behavior, documented lossiness, dependency records, redaction review, provenance, and a clear status. Promotion requires a human-authorized commit or an explicitly authorized automated write. Runtime execution requires a separately reviewed deployment boundary.
