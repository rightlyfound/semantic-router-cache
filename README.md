# semantic-router-cache

Versioned cache and provenance store for the Semantic OS workflow. Validated adapters, schemas, fixtures, skill manifests, and redacted audit records live here.

The repository is a source of truth and review surface, not a production runtime or low-latency queue.

The maintained implementation roadmap and ready-to-run engineering prompts are in [`docs/roadmap-and-prompts.md`](docs/roadmap-and-prompts.md). Follow the roadmap in order; do not treat the prompt pack as permission to create schedules, push branches, open issues, or deploy services without explicit authorization.

## Scheduling Notes

Scheduled tasks run in the platform’s effective timezone: **Australia/Sydney**, UTC+10/UTC+11 with daylight saving.

For Brisbane users (**Australia/Brisbane**, UTC+10 year-round):

- During standard time, approximately April–September, tasks execute at the scheduled local time.
- During Sydney daylight-saving time, approximately October–March, a task scheduled for 09:00 Sydney time executes at 08:00 Brisbane time.

To avoid ambiguity, all task instructions include an explicit timezone reference. The current Schema Drift Monitor remains configured for Mondays at 09:00 in the platform’s effective Australia/Sydney timezone.
