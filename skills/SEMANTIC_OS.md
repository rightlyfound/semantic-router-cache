# SEMANTIC_OS — Platform-Native Semantic Router for Manus

## Purpose

Build a reusable workflow named **SEMANTIC_OS** that translates a source artifact into a target contract, validates the translation, preserves provenance, and reuses successful mappings. The system should support data-shape mapping, API-contract translation, code-porting, documentation drift analysis, and abstract-intent-to-tool routing.

The workflow must use the capabilities that are actually available in the current Manus session. Treat GitHub, Context7, OpenRouter, and scheduling as integrations that must be inspected and used through their available interfaces; do not assume that a particular connector, endpoint, model name, or permission exists until verified.

## Operating principles

1. **Inspect before acting.** Check the current session configuration and available tools before using an integration. If an integration is unavailable, explain the limitation and offer the closest viable fallback.
2. **Cache before synthesis.** Look for a previously validated adapter using a deterministic identity. Reuse it only when the source and target fingerprints, dependency versions, and adapter policy are compatible.
3. **Use authoritative context.** Query Context7 for current, library-specific documentation when the target depends on a library, framework, protocol, or tool schema. Prefer official repository or specification sources for custom interfaces.
4. **Use model routing dynamically.** Use the OpenRouter integration or API that is actually available. Select a model based on the task’s capability needs, context length, latency, and current availability. Do not hard-code a model that has not been verified in the live catalog. Record the selected model and the reason for selection.
5. **Validate before execution.** Treat generated code and mappings as untrusted until reviewed, statically checked, and executed only in a controlled sandbox against representative fixtures. Never run destructive operations, network calls, credential access, or production writes during validation.
6. **Make writes explicit and auditable.** Before changing a GitHub repository, identify the repository, branch, files, and intended diff. Preserve existing user content, avoid overwriting unrelated changes, and report the resulting commit or pull request. If the current interface requires confirmation for a write, pause for confirmation.
7. **Fail safely.** If validation fails, perform at most one targeted repair attempt. If the repair fails, preserve the failing fixture and diagnostics in the audit record and do not cache the result as valid.
8. **Protect secrets and sensitive data.** Never place API keys, OAuth tokens, credentials, or raw sensitive payloads in generated source, commits, issue bodies, logs, prompts, or audit files. Redact sensitive values before persistence.
9. **Be honest about persistence.** A GitHub repository is the source-controlled cache and audit store. It is not, by itself, a runtime, queue, database, or low-latency service. Recommend a deployed service only when the user needs continuous, high-volume, or low-latency execution.

## Repository setup

Use the GitHub integration available in this session to locate a repository named `semantic-router-cache` under the user’s account. If it does not exist, propose creating it as a **private repository** and proceed only if the current workflow permits the write. Do not create a duplicate repository with a similar name without checking first.

Create or maintain this layout:

```text
semantic-router-cache/
├── adapters/                 # Validated adapter implementations and metadata
├── schemas/                  # Canonical source, target, dependency, and intent records
├── skills/                   # Versioned workflow manifests and sub-skill definitions
├── audit/                    # Redacted provenance, validation, and failure records
├── fixtures/                 # Safe, minimal test fixtures; never store secrets
├── scheduled/                # Optional schedule playbooks and manifests
├── README.md
└── .gitignore
```

Use JSON for machine-readable records and Markdown for human-readable manifests. Keep adapter code and adapter metadata together where practical, for example:

```text
adapters/{adapter_id}/adapter.py
adapters/{adapter_id}/manifest.json
```

When several repository reads are needed in one task, prefer a local working copy in the session workspace: clone or fetch once, perform read-only cache lookups locally, and synchronize only the intended final changes. Treat the local copy as an ephemeral acceleration layer, not as the source of truth. Before any push or commit, refresh from the target branch and check for conflicting changes. If cloning is unavailable, fall back to the repository integration and note the additional round trips.

## Canonical identity and cache policy

For every bridge, normalize the following values into canonical JSON with stable key ordering and normalized line endings:

- Source kind, schema or signature, relevant version, and dependency identifiers.
- Target kind, schema or signature, relevant version, and dependency identifiers.
- Mapping policy, including null handling, coercion rules, units, timezone policy, and lossiness policy.
- Validation policy, including JSON Schema, Pydantic, TypeScript, OpenAPI, GraphQL, protobuf, or custom checks.

Compute a SHA-256 digest for the canonical source record and the canonical target record. Define:

```text
adapter_id = sha256(source_record)[:16] + "_" + sha256(target_record)[:16]
```

The adapter cache is valid only when the stored manifest matches the requested policy and dependency versions. If a dependency or contract changes, mark the adapter **stale** rather than silently using it.

## Master workflow: `/SEMANTIC_OS`

When the user invokes `/SEMANTIC_OS`, follow these stages.

### Stage 0 — Clarify the bridge

Identify the source artifact, target requirement, validation authority, expected output, and whether the user wants a preview, a committed artifact, or execution against a real payload. Ask only questions that change the implementation or safety boundary. If the source or target is ambiguous, do not invent a schema.

### Stage 1 — Fingerprint

Extract the source and target representations. For data, capture key topology, types, requiredness, examples, and semantic annotations. For code, capture language, function or class signatures, imports, and a structural fingerprint; do not rely on a raw text hash alone. For APIs, capture method, path, request and response shapes, authentication requirements, and protocol version.

Write redacted canonical records to `schemas/` when persistence is requested. Never persist raw secrets or unnecessary personal data.

### Stage 2 — Cache lookup

Search GitHub for the computed `adapter_id`. Read the adapter manifest and validation history if present. Reuse the adapter only if its dependency versions, mapping policy, and validation authority are compatible. If the adapter is stale, explain why and continue to context gathering.

### Stage 3 — Context gathering

If the target involves a known framework, library, protocol, or external tool, query the available Context7 MCP for current documentation and implementation examples. Prefer precise queries containing function names, type signatures, endpoint names, or version identifiers over broad topic queries. Retrieve only the material needed for the mapping. Record source titles, library versions, URLs or reference identifiers, and the relevant conclusions. If the lookup is unavailable, times out, or returns no relevant material within a reasonable per-query limit, continue only when the task can be completed safely from the supplied contract and clearly record the omission in the audit log; otherwise stop and ask for an authoritative source.

For a custom MCP or repository-defined interface, inspect the tool schema or the specified GitHub files directly. Do not use Context7 as a substitute for a private repository’s source of truth.

### Stage 4 — Synthesis

Choose the available model or provider dynamically. Use a stronger reasoning model for ambiguous architectural contracts, a code-oriented model for deterministic transformations, and a long-context model for large specifications. If a live model catalog is available, use it to confirm model availability and capabilities before selection.

**Output capacity check:** Before selecting a model, verify its available `max_completion_tokens` or per-request output limit in the live catalog. Prefer models with at least 4,000 available output tokens for adapter synthesis. Use this priority when the listed model IDs are available and their output capacity is sufficient:

| Priority | Model | Minimum output | Use when |
|---|---|---:|---|
| 1 | `anthropic/claude-sonnet-4` | 8,192 | General adapter synthesis |
| 2 | `deepseek/deepseek-chat` | 8,192 | Fast, deterministic transformations |
| 3 | `google/gemini-1.5-pro` | 8,192 | Large schema ingestion |
| 4 | `anthropic/claude-haiku-4` | 4,096 | Simple mappings or budget-constrained work |
| 5 | `meta-llama/llama-3.1-70b` | 8,192 | Open-model fallback |

Treat these as preferences rather than guarantees; verify live availability, supported parameters, context length, and effective output capacity. Avoid any model or tier with fewer than 2,048 output tokens for ordinary adapter synthesis. If the highest-ranked available option has fewer than 2,000 output tokens, switch to **two-pass synthesis**: Pass 1 generates only the `translate(data)` function body, with no docstring, explanation, or tests. Pass 2 generates the test suite separately, referencing the function from Pass 1. When this mode is used, record `synthesis_mode: "two_pass"` in the adapter manifest. If even the function-only pass cannot fit, fail safely and do not cache the result.

Ask the model to produce:

1. A short mapping explanation and explicit assumptions.
2. A pure, deterministic adapter with a narrow interface such as `translate(data) -> dict` unless the target requires another interface.
3. Explicit behavior for missing, null, extra, malformed, and conflicting fields.
4. Unit normalization, timezone handling, precision, and lossiness decisions.
5. A compact test suite or test cases derived from the source and target contracts.
6. No network access, filesystem writes, subprocesses, dynamic imports, credential access, or hidden side effects unless the user explicitly requests an integration adapter and the operation is reviewed separately.

### Stage 5 — Review and validation

Prefer structured output when the selected model and endpoint reliably support it. If strict JSON mode is unavailable or produces malformed output, fall back to ordinary text completion and parse only a clearly delimited fenced code block or explicitly labeled sections. Reject ambiguous or multiply-defined outputs rather than guessing. Preserve the raw model response only in temporary workspace storage unless the user explicitly requests it and it contains no sensitive data.

Before execution, inspect the generated artifact for unsafe imports, dynamic code execution, hidden I/O, credential references, destructive operations, and non-deterministic behavior. Then run it in an isolated validation environment against safe fixtures.

Validate the result against the authoritative target contract. Check both positive and negative cases, including missing fields, null values, wrong types, boundary values, malformed timestamps, and unexpected extra fields when relevant. For lossy mappings, report exactly what was discarded or approximated. When the reverse mapping is semantically meaningful and can be defined without inventing unavailable information, run an optional **round-trip fidelity test**: apply the forward adapter, apply a separately defined reverse adapter, and compare the recovered source with the original under an explicit equivalence policy. Treat unrecoverable fields as documented lossiness, not as a validation pass. Do not require round-trip identity for intentionally one-way, aggregating, privacy-preserving, or inherently lossy transformations.

If validation fails, perform one repair synthesis with the concrete error and failing fixture. If it fails again, write a redacted failure record to `audit/{adapter_id}_fail.json`, do not cache the adapter as valid, and report the failure with a recommended next action.

### Stage 6 — Cache and provenance

On successful validation, prepare the adapter and manifest for GitHub. The manifest should include:

```json
{
  "adapter_id": "...",
  "created_at": "RFC3339 timestamp",
  "source_fingerprint": "...",
  "target_fingerprint": "...",
  "mapping_policy": {},
  "dependency_versions": {},
  "validation_authority": "...",
  "models_used": [],
  "synthesis_mode": "single_pass",
  "context_references": [],
  "fixture_ids": [],
  "test_result": "passed",
  "lossiness": [],
  "redactions": [],
  "status": "valid"
}
```

Commit only the intended files, using a clear commit message such as `cache: add validated adapter {adapter_id}`. When multiple files are involved, use one logical batched commit if the available GitHub interface supports it. If only individual file writes are available, write the complete set, report that the history may contain multiple commits, and provide a consolidated diff summary. Before committing, refresh the target branch and detect conflicts. If the user requested preview-only mode, show the proposed files and diff without committing.

### Stage 7 — Execute, if requested

Run the validated adapter against the user’s real payload only after the user has requested execution. Return the target-shaped result, validation status, assumptions, and any lossiness warnings. Do not automatically call external tools, write to production systems, send notifications, or modify third-party data unless that action is explicitly requested and confirmed when required.

## Sub-skills

### `/API_BRIDGE`

Use for REST-to-REST, REST-to-GraphQL, REST-to-gRPC, webhook-to-domain-model, and similar contract translations. Obtain the authoritative target schema first. Preserve authentication boundaries: a schema bridge should not receive or emit credentials. Store only redacted OpenAPI, GraphQL, protobuf, or webhook fragments needed for reproducible validation.

### `/CODE_PORT`

Use for translating a function, type, or module between languages or runtimes. Read the exact source file and relevant tests from the specified repository. Preserve behavior rather than merely translating syntax. Record source and target language versions, public signatures, dependency assumptions, and structural fingerprints. Return generated code separately from the explanation and do not commit until validation passes.

### `/DOC_SYNC`

Use when the user names a library, framework, protocol, or version and wants drift analysis. Retrieve current documentation from the authoritative available source, compare it with the cached record in `schemas/`, and produce a concise diff. Search adapter manifests for dependency references and mark affected adapters as `stale`. Do not regenerate adapters automatically unless the user explicitly asks for regeneration.

### `/AGENT_PROTOCOL`

Use when the user provides an abstract intent such as “notify the team about a deployment.” Search the intent registry for available integrations and tool schemas. Prefer an existing validated intent adapter. If none exists, produce a proposed mapping and identify the exact tool, arguments, side effects, and approval boundary. Cache only after validation. Never infer permission to send messages, spend money, delete data, or alter production systems from the abstract intent alone.

## Intent registry

Maintain `schemas/intent_registry.json` with entries shaped like:

```json
{
  "intent": "notify_team_about_deployment",
  "description": "Send a deployment notification to a specified team destination.",
  "candidate_integrations": [],
  "tool_schema_reference": "...",
  "required_inputs": ["message", "destination"],
  "side_effects": ["send_message"],
  "approval_required": true,
  "adapter_id": "...",
  "status": "proposed"
}
```

Keep the registry provider-neutral. Store connector names, tool names, and argument schemas only after discovering them from the current integration. Do not hard-code credentials, private tokens, or undocumented endpoints. Keep active entries limited to `valid`, `stale`, and `proposed` records. Move `deprecated` or `superseded` entries older than 90 days into `schemas/intent_registry_archive.json`, retaining their IDs, replacement references, and historical audit links. Archive conservatively and never delete historical provenance.

## Scheduling and maintenance

Do not create recurring schedules as an incidental side effect of installing the skill. Offer maintenance schedules as an explicit, separate setup step. Because a task may have a schedule limit, use separate maintenance tasks when the platform requires it, or combine checks into one low-frequency maintenance playbook when appropriate.

The recommended maintenance playbooks are:

**Schema Drift Monitor:** At a user-approved low frequency, inspect the dependency and intent records, query authoritative documentation, compare normalized records, and create a GitHub issue only when a material change is detected. Include a redacted diff and affected adapter IDs. Mention the user only when their GitHub username or notification preference is known and the user has requested it.

**Adapter Health Check:** At a user-approved low frequency, enumerate valid adapters, run their safe fixtures, and mark failures as stale. Create an issue with the adapter ID, failing test summary, dependency versions, and a link to the audit record. Never run an adapter against production payloads during a health check.

Schedules must be timezone-aware, idempotent, and safe to retry. State the timezone and expected execution cost or operational tradeoff before enabling them.

## Example execution

Bridge this payload to the internal weather observation format.

Source:

```json
{
  "cloud_density": 85,
  "coords": [40.7, -74.0],
  "timestamp": "2026-08-30T08:17:00+10:00"
}
```

Target:

```text
{
  "sunlight_intensity": float,  // 0.0 to 1.0
  "lat": float,
  "lng": float,
  "recorded_at": datetime ISO8601
}
```

For this example, do not imply that a meteorological lookup is required unless an external scientific convention is being used. Under the stated simplified rule, document the assumption `sunlight_intensity = 1 - cloud_density / 100`, map `coords[0]` to `lat`, map `coords[1]` to `lng`, and preserve the timestamp as an ISO 8601 value with its offset. Validate the range and timestamp format, then show:

1. The computed `adapter_id` and the canonical fingerprint inputs.
2. The Context7 lookup, or an explicit statement that no lookup was necessary.
3. The selected model or provider and the capability-based reason for selection.
4. The generated `translate()` implementation.
5. The validation cases and results.
6. The proposed or completed GitHub diff and commit reference, clearly distinguishing preview from committed state.
7. Any assumptions, warnings, or lossy transformations.

## Installation and invocation contract

Store this manifest at `skills/SEMANTIC_OS.md` in the cache repository. Treat that file as the versioned workflow definition, not as an automatically registered platform skill. When the user invokes `/SEMANTIC_OS`, first read the manifest from GitHub if the repository is configured and reachable; otherwise use the latest user-provided copy and report that fallback.

The user may invoke the system with a request such as:

```text
/SEMANTIC_OS
Source: Stripe webhook payload pasted below.
Target: PaymentEvent model in mycompany/backend/models/payment.py.
Mode: preview and validate; do not commit or send data.
```

The response must always distinguish **discovered facts**, **assumptions**, **generated artifacts**, **validation results**, **side effects**, and **next actions**. This distinction is part of the system’s reliability contract.

## Boundaries and upgrade path

This design is appropriate for agent workflows, developer tooling, and low-volume contract translation. It is not a substitute for a production runtime when the user needs millisecond latency, high-throughput streaming, strict service-level objectives, multi-user concurrency, or continuous event processing. In those cases, keep GitHub as the reviewed source of truth but deploy the validated adapters behind a conventional service, queue, database, or cache selected for the workload.
