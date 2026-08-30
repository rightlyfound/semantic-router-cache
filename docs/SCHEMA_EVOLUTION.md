# Schema evolution policy seed

This file records the initial schema versioning policy for adapter manifests.

Seed policy:
- `schema_version` must be present in every manifest. Seed: `2026-08-1`.
- Patch (non-breaking) changes: increment last component (e.g., `2026-08-2`).
- Minor (additive, backwards-compatible) changes: increment month or second component.
- Breaking changes require a migration plan and must be documented in the PR.

Migration guidance:
- Provide scripts or examples to migrate old manifests into the new format.
- Include tests that demonstrate backward compatibility when claimed.
