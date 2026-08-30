# Semantic Router Quality and Test Coverage Report

**Prepared for:** Stakeholder review  
**Project:** `rightlyfound/semantic-router-cache`  
**Review date:** 30 August 2026  
**Latest implementation commit:** [`0c1bda6`](https://github.com/rightlyfound/semantic-router-cache/commit/0c1bda6d8e7bf517de6a4a44a17808cb94958616)

## Executive summary

The Semantic OS repository has moved from a lightly tested adapter cache to a guarded, reviewable engineering surface. The latest verification run completed **30 tests with no failures**, achieved **94% statement coverage** across the models, utility scripts, and adapters, and passed linting, manifest validation, adapter-index consistency checks, and redaction scanning.

Coverage increased from **77% across 13 tests** to **94% across 30 tests** after dedicated tests were added for the utility command-line programs and previously under-tested adapter failure branches. This materially improves confidence in deterministic repository operations, but it does not by itself establish production-runtime properties such as continuous availability, zero-loss delivery, or fixed latency.

## Verification results

| Quality gate | Latest result | Stakeholder interpretation |
|---|---:|---|
| Test suite | **30 passed** | All automated test cases completed successfully |
| Overall statement coverage | **94%** | Above the project target of 90% |
| Manifest validation | Passed for 2 adapter manifests | Cached metadata conforms to the project contract |
| Derived adapter index | Current | Index matches the canonical adapter directories and manifests |
| Redaction scan | Passed | No high-confidence credential patterns detected in scanned audit and fixture files |
| Ruff lint | Passed | No configured lint violations remain |
| Adapter syntax compilation | Passed | Python adapter files compile successfully |
| Coverage artifact | Generated | HTML and JSON reports are available for detailed review |

The run used `pytest` with `pytest-cov`, the project’s manifest validator, the reproducible index checker, the redaction scanner, and Ruff. The test framework and coverage tooling are standard development tools; the project-specific acceptance evidence is recorded in the repository commit and generated reports.[1] [2] [3]

## Coverage by component

| Component | Statements | Covered | Coverage | Main remaining gaps |
|---|---:|---:|---:|---|
| Webhook adapter | 22 | 20 | 91% | Two required-field error branches |
| Weather adapter | 21 | 18 | 86% | Three type/shape error branches |
| Adapter manifest model | 53 | 50 | 94% | Two invalid enum validators and one fallback error path |
| PullRequestEvent model | 17 | 17 | 100% | None identified |
| `compute_adapter_id.py` | 35 | 34 | 97% | Module entry-point exit line |
| `redaction_check.py` | 31 | 30 | 97% | Module entry-point exit line |
| `update_index.py` | 50 | 47 | 94% | Duplicate-ID and temporary-file cleanup branch |
| `validate_manifest.py` | 23 | 21 | 91% | Direct entry-point and one error branch |
| **Total** | **252** | **237** | **94%** | Focused, low-risk edge branches remain |

Coverage is a measure of executed statements, not a proof that every semantic outcome is correct. The strongest evidence comes from combining coverage with contract validation, negative tests, deterministic fixtures, and redaction checks.

## Improvements delivered

### Contract enforcement

The repository now has a machine-readable adapter-manifest JSON Schema and a matching Pydantic v2 model. The contract covers schema versioning, deterministic identity fields, synthesis mode, validation authority, dependency records, fixture references, lossiness, redactions, and lifecycle status. A command-line validator returns structured output and non-zero status for invalid manifests.

### Deterministic discovery and reuse

The repository now provides a canonical adapter layout under `adapters/{adapter_id}/`, a deterministic adapter-ID utility, and a reproducible derived index. The index can be regenerated or checked without mutation, reducing lookup ambiguity and preventing manually maintained metadata from drifting away from the actual adapter directories.

### Utility-script reliability

Dedicated tests now exercise normal and error paths for all utility command-line programs. These include missing arguments, manifest identity mismatches, invalid index state, missing adapter files, empty repositories, default scanner paths, explicit scanner paths, binary files, Python bytecode files, and multiple high-confidence secret detectors.

### CI and governance

A consolidated least-privilege CI workflow now performs syntax checks, manifest validation, index verification, redaction scanning, linting, and tests. Contributor guidance, schema-evolution policy, a tutorial, a pull-request template, and a declarative maintenance-playbook record were added. The guidance distinguishes preview from promotion and prevents repository documentation from implying unsupported production capabilities.

### Adapter safety

The webhook and weather adapters are validated against safe fixtures, and the webhook adapter is validated against the `PullRequestEvent` Pydantic model. Negative tests cover malformed payloads and invalid field shapes. The redaction scanner is deliberately conservative: high-confidence credential patterns fail the check, while ordinary fixture emails and realistic sample values are not automatically treated as secrets.

## Coverage improvement

| Measurement point | Tests | Overall coverage |
|---|---:|---:|
| Initial baseline | 13 | 77% |
| After dedicated CLI and branch tests | 30 | **94%** |
| Improvement | +17 | **+17 percentage points** |

The largest gain came from testing the previously under-covered CLI entry points and repository mutation/check branches. The result exceeds the stated 90% target without resorting to blanket exclusions or weakening the quality gates.

## Residual risks and limitations

The remaining uncovered statements are mostly narrow error or process branches, particularly adapter field failures and module entry-point lines. They are not evidence of a defect, but they are appropriate candidates for incremental hardening if the adapters become more important.

The repository is still a source-controlled cache and audit surface rather than a production data plane. Passing tests do not demonstrate streaming durability, packet buffering, atomic hot-swapping, rollback, service-level latency, multi-tenant isolation, or continuous processing. Those capabilities require a separately deployed runtime and additional operational tests.

The local working tree still contains two intentionally unpromoted historical artifacts: the incomplete webhook synthesis candidate and its failure audit. They were excluded from the quality-improvement commit so an incomplete adapter could not be mistaken for a valid cached artifact. The coverage database and HTML output are also generated local artifacts rather than source files.

## Recommended next steps

The immediate recommendation is to keep the current gates unchanged and observe the combined maintenance schedule before expanding the adapter catalog. After that observation, add a low-risk API bridge in preview mode, including dependency checks for `EmailStr`, explicit phone-number lossiness, missing nested sections, and malformed email cases.

If the project later moves toward runtime execution, the next quality milestone should be an operational-readiness review covering bounded buffering, atomic adapter activation, rollback, retries, idempotency, observability, authorization, and data retention. Code coverage should remain a supporting measure rather than the sole release criterion.

## Evidence and reproducibility

From the repository root, stakeholders or reviewers can reproduce the core checks with:

```bash
pytest -q --cov=models --cov=scripts --cov=adapters --cov-report=term-missing
ruff check models scripts tests adapters
python3 scripts/validate_manifest.py adapters/*/manifest.json
python3 scripts/update_index.py --check --root .
python3 scripts/redaction_check.py audit fixtures
```

The detailed HTML coverage report is generated at `coverage_html/index.html`, and the machine-readable report is generated at `coverage.json`.

## References

[1]: https://docs.pytest.org/ — Pytest documentation  
[2]: https://coverage.readthedocs.io/ — Coverage.py documentation  
[3]: https://docs.astral.sh/ruff/ — Ruff documentation  
[4]: https://github.com/rightlyfound/semantic-router-cache/commit/0c1bda6d8e7bf517de6a4a44a17808cb94958616 — Utility CLI coverage test commit  
[5]: https://github.com/rightlyfound/semantic-router-cache/commit/c68d9ec2b3ca21520cbea83a2d9a8e30ce586bc7 — Guarded adapter tooling and repository CI commit  
