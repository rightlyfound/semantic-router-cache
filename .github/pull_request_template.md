## Summary

Describe the adapter, manifest, documentation, or tooling change.

## Validation checklist

- [ ] Source and target contracts are explicit and free of secrets.
- [ ] Manifest validation passes.
- [ ] Adapter index is current.
- [ ] Positive and negative tests pass in isolation.
- [ ] Redaction scan passes for audit and fixture changes.
- [ ] Lossiness, optional fields, coercions, dependencies, and timezone behavior are documented.
- [ ] Generated code was reviewed and contains no unapproved I/O or side effects.
- [ ] This change does not create or modify schedules, external issues, messages, or production writes without explicit authorization.

## Promotion boundary

State whether this is preview-only, validation-only, or approved for cache promotion. Include the audit record and fixture IDs.
