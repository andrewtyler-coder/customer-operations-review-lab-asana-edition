# Architecture and limitations

Synthetic JSON -> exact evidence matcher -> proposals / exception queue -> human review -> payload-specific approval -> stale-value check -> in-memory mock write -> audit entry.

The command line stops at the review queue. Only tests call approve/apply. This keeps the demonstration safe to run and makes the intended human decision boundary explicit, the same boundary Asana draws around AI Teammates: the agent drafts, a person approves each exact change, and ambiguous work escalates.

Exact duplicate evidence is collapsed by a canonical JSON hash. Different records, including contradictory copies with the same source ID, are deliberately treated as ambiguous and routed to the exception queue. Proposal hashes cover task GID, field, expected value, proposed value and evidence ID. An approved change cannot silently become a different change.

## Component map

- `workflow.py`: conservative custom-field proposals on account tasks, the exception queue, payload-bound mock approval and idempotent mock application with an audit record.
- `operations.py`: deterministic planning helpers - form-intake coverage, renewal-signal triage, task-change attention, account review preparation, post-engagement proposal formation, portfolio health rollup, workflow-to-capability mapping, 30/60/90 adoption benchmarks, and handoff-manifest recomputation.
- `system.py`: `CSWorkspaceCycle` composes these into one synthetic day: start-day coverage, account review preparation, attested check-ins, post-engagement work, draft handoff narratives and end-of-day review.

## Deliberate simplifications

- Trusted fixture input, not an ingestion API with schema validation.
- Exact periods and field names, not timezone-aware/fuzzy matching.
- One in-memory process, not durable idempotency across restarts.
- No approval identity, authorization, expiry, revocation or signed approval tokens.
- No atomic transaction between write and audit; no failure recovery for remote writes.
- Source evidence changes after approval are not checked, only the destination's expected value.
- Only single custom-field enrichment is modeled; no multi-field transactions, sections moves, assignments or comments.
- Signal thresholds (utilization floor, support ceiling, benchmark plan) are caller-supplied configuration, not learned or recommended values.
- The capability map encodes public rules of thumb (AI Studio for high-volume repeatable work, AI Teammates for judgment work, MCP for cross-system work); it does not evaluate a real workspace.

Before a real deployment: validate schemas; implement authenticated role-based review; bind approvals to evidence versions and expiration; use transactional persistent storage; define retry semantics and reconciliation; redact telemetry; restrict field and workspace scopes; connect through Asana's MCP server or REST API with organization-approved OAuth; add integration tests against a sandbox workspace; and review privacy, security and ownership requirements. These are requirements, not completed features.

## Expanded offline cycle

The cycle scopes records to its configured book of business. Account review preparation deduplicates intake and excludes records after the cutoff; its historical context may predate the alert window. A failed refresh invalidates the prior coverage report. Missing tasks remain in the returned merged baseline pending verification. Check-ins are recorded only from explicit caller attestations with evidence IDs, not authenticated proof or inferred from a prepared summary. Handoff review recomputes counts and hashes; it does not post, approve or validate a real audience.

