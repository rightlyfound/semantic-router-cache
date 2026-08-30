# Schema evolution policy

The manifest contract is versioned by `schema_version`. A compatible change adds optional metadata or a non-breaking field with a documented default. A breaking change removes or changes the meaning of a field, changes requiredness, changes status semantics, or alters adapter identity rules.

Breaking changes require a migration script or explicit migration instructions, validation of every valid adapter, and a reviewed pull request. Existing audit records remain immutable. Adapters affected by dependency or contract changes are marked `stale`; they are never silently reused.

Adapter statuses follow these transitions:

| Current | Allowed next state | Condition |
|---|---|---|
| proposed | valid or invalid | Validation completed |
| valid | stale or deprecated | Contract/dependency drift or intentional retirement |
| stale | valid or invalid | Revalidation completed |
| invalid | proposed or deprecated | Repair/replacement decision is reviewed |
| deprecated | archived | Replacement and audit references are recorded |

When the canonicalization algorithm changes, increment its version and treat all existing IDs as requiring migration review. Never rewrite history to hide an old identity.
