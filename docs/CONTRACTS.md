# Demo contract, version 1

Fixtures are UTF-8 JSON. The current code consumes trusted local fixtures; these contracts document shape, not a validated public API, and not Asana's real API shapes. Field names are Asana-flavored (gid, custom_fields, due_on, section) for readability only.

`account_tasks`: list of records with unique `gid`, `account_id`, `name`, `period` (e.g. "2030-Q1"), and `custom_fields` (an object whose values are null, empty string, or nonempty string). Optional `last_reviewed_at`: timezone-aware ISO timestamp or null.

`evidence`: list of records with `id`, `account_id`, `field`, `period`, and `value` (nonempty string for useful evidence). All values are synthetic. Identical records may repeat; contradictory records remain distinct and require review.

`submissions` (intake helpers): records with unique `gid`, `account_id`, `created_at` (timezone-aware ISO timestamp) and content fields.

`signals` (triage helper): records with `account_id`, `period`, `utilization` (0..1 or null), `retention_score` ('red'/'yellow'/'green' or null), `qualitative` (list of strings), `support_tickets` (int or null).

`usage_rows` (adoption helper): records with `account_id`, `day` (30, 60 or 90), `active_workflows` (int or null), `ai_requests` (int or null). `plan`: object mapping '30'/'60'/'90' to non-negative integer targets.

`workflows` (capability helper): records with unique `id`, `name`, `volume` ('high'/'low'), `structure` ('repeatable'/'judgment'), `systems` (list of strings).

Review output:
- `mode`: explicit review-only status.
- `proposals`: objects containing `task_gid`, `field`, `expected`, `proposed`, and `evidence_id`.
- `exception_queue`: objects with `task_gid`, `queue` and `reason`.

The prototype does not validate all types, untrusted text, field lengths, normalized dates or missing keys. Production ingestion needs explicit schema validation and access controls before using these shapes. Do not infer that Asana's API or MCP server accepts them directly; the real tool schemas come from the platform's own documentation and `tools/list`.

