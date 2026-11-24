# Capability map and adoption roadmap

This package includes a complete **synthetic local CS workspace cycle** on Asana-shaped records, configurable operating guidance and agent task templates. It is not an installed production system and not connected to Asana. The following distinctions are essential.

| Workflow | Implemented offline | Still requires integration or development |
| --- | --- | --- |
| Form intake coverage | Exact window, supplied book-of-business filtering, stable-GID deduplication, incomplete-read warning | Real form/submission reads via API or MCP, pagination, state persistence, notification delivery |
| Renewal signal triage | Caller-configured thresholds across utilization, retention score, qualitative and support signals; missing data escalates | Live usage/support data feeds, data-science score access, durable flag storage, review cadence scheduling |
| Portfolio health rollup | Supplied task rollup, unknown-stays-unknown, unreviewed-account surfacing | Real portfolio reads, verified review-story lookup, durable reporting |
| Workflow-to-capability mapping | Rule-of-thumb candidate proposals (AI Studio / AI Teammate / MCP / manual) | Real process discovery, cost and governance review, admin enablement |
| Adoption benchmarks | 30/60/90 target comparison on supplied usage rows; absent data never marks an account behind | Real AI-request/workflow usage data, agreed baselines, business-review packaging |
| Task attention | Separate baseline comparison, actual assignee, new/material/newly-due alerts, missing-task verification flag | Live task reads, durable baseline, verified completion lookup |
| Account review preparation | Supplied recent stories, open tasks, unresolved decisions and coverage status | Calendar/CRM/Asana adapters, evidence freshness policy |
| Post-engagement proposals | Explicit human-labeled commitment handling with owner/evidence | Transcript access and extraction, real task creation and approval |
| Check-ins | Evidence-ID-required caller-attested mock state, separate from summaries | Real completion evidence verification and authorization |
| Handoff narratives | Exact current draft count and manifest hash for comment/status-update drafts | Authenticated approval, posting adapters, delivery reconciliation |
| Field reconciliation | Conservative exact evidence matching, conflict queue, payload-bound mock approval and idempotent application | Durable authorization, persistence, concurrency and live write adapters via MCP or REST |
| SOD/EOD cycle | `system.CSWorkspaceCycle` aggregates coverage, proposals, current drafts, unresolved decisions and mock audit | Scheduling, durable multi-day handoff, real reporting/delivery |
| Follow-up cadence | Verified-touch tracking, first-trigger vs repeat entry, ladder escalation, verified-response stop, approval-gated status proposals | Live outreach/response reads, durable cadence state, real messaging approvals |
| Action approval protocol | Exact-payload approval, apply-once, read-back verification, uncertainty blocks retry until human reconciliation | Authenticated approvals, durable attempt state, live write adapters |
| Evidence hierarchy | Exact-ID primary match, labeled documented fallback, shareable-link enforcement, incomplete reads forbid "latest" | Real source adapters, permission-aware link verification |
| Open loops and closeout | Carryover queue with owner/due/evidence, submit-once closeout with saved-state verification | Durable loop storage, real form/report submission and read-back |
| Weekly reporting | Operating specification | Aggregation implementation, verified outcome metrics |

## Demonstrations

- `python3 workflow.py`: reconciliation proposals and the exception queue only.
- `python3 demo_operations.py`: deterministic local planning helpers including triage, portfolio health, capability mapping and adoption benchmarks.
- `python3 demo_system.py`: full synthetic cycle across the local components.
- `python3 demo_followthrough.py`: follow-up cadence, coverage-accounted brief, approval-bound actions, evidence hierarchy, open loops and closeout verification.
- `python3 -m unittest discover -s tests -v`: run the current suite. Inspect actual output; do not infer adapter support from a unit-test pass.

## Critical lifecycle boundaries

A completed summary does not complete a check-in. The local system records check-ins separately and labels them caller-attested. Unresolved decisions survive the local handoff. Draft counts and hashes are recalculated from current content. Flags and candidates are review material, not automated account changes. These are local behaviors, not authenticated production guarantees.

## Adoption sequence

1. Run the entire offline cycle and inspect tests and outputs.
2. Complete the book-of-business configuration checklist in OPERATING_PLAYBOOK.md.
3. Implement read-only sandbox adapters (Asana MCP server or REST API) and test identity, pagination, timestamp boundaries and failed reads.
4. Produce reviewable proposals from sandbox evidence. Test conflicting values, ambiguous matches, missing pages, stale data, and duplicates.
5. Implement a separate write adapter with explicit authorization, durable audit state, readback, concurrency protection, and uncertain-outcome handling.
6. Run a small approved pilot and reconcile every outcome. Expand only after review of failures and coverage.

Use AGENT_TEMPLATES.md for cold-start assignments, SOURCE_SAFETY.md for evidence/permissions boundaries and PORTABILITY.md for runtime requirements. No deployment, universal provider compatibility, Asana endorsement, compliance certification or measured business impact is implied.

