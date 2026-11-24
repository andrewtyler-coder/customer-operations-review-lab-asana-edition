# Cold-start agent task templates

These prompts are reusable task specifications, not permission grants or provider-specific installers. Replace angle-bracket fields with approved configuration. Do not insert secrets into prompts.

## Initial onboarding

> Read README.md, AGENTS.md, docs/ARCHITECTURE.md, docs/OPERATING_PLAYBOOK.md and docs/PORTABILITY.md. Inspect the implementation and run the documented tests and all documented offline demonstrations. Return supported capabilities, test results, missing integrations and proposed next steps. Use only synthetic inputs. Do not connect accounts, upload data, send messages or change external records. Distinguish implemented helpers from specification-only workflows. Ask only for information that blocks the next authorized step.

## Read-only daily review

> Prepare a start-of-day review for <approved book of business> through <cutoff with timezone>. Use <approved sources> and <verified checkpoints>. Resolve current ownership, retrieve all pages, locally filter exact timestamps, deduplicate stable submission IDs, run renewal-signal triage with the configured thresholds, and compare tasks with their separate baseline. Label actual task assignees. Preserve unresolved decisions and failed coverage. Do not infer completion from a missing task or health from a blank field. Return priorities with source links and proposed next steps. Do not post comments or make external changes. If adapters are unavailable, report that limitation rather than pretending to inspect live data.

## Account review preparation and post-engagement proposals

> For <verified account and meeting>, prepare an evidence-linked briefing from <authorized sources>. Separate facts, open commitments, unresolved decisions and proposed questions. A briefing does not complete a check-in. After authorized meeting evidence is provided, propose actions only from explicit commitments, naming their actual owners and any stated due dates. Flag incomplete or ambiguous statements. Draft any comment or status update for review; do not create tasks, update custom fields or post it.

## Renewal-risk triage review

> Run signal triage for <approved accounts> over <period> using <approved thresholds>. Show each flag with its exact reasons and source signals. Escalate missing or contradictory signal data; never fill gaps by inference. Return the flag list and the escalation list for human review. A flag is a reason to review the renewal, not an account change.

## Adoption benchmark review

> Compare <supplied usage rows> against the agreed 30/60/90 plan. Report on-track and behind accounts with actual numbers and targets. Escalate missing usage data; never mark an account behind on absent data. Note that benchmarks measure adoption, not business outcomes.

## Reconciliation review

> Review <approved custom fields> for <account scope> against <approved evidence>. Show current value, proposed value, exact match basis and source for every proposal. Leave missing evidence unresolved; hold conflicts and ambiguous matches in the exception queue. Do not guess values or overwrite existing data. Return the exact proposed change set for human review. No live changes are authorized by this prompt.

## End-of-day handoff

> Summarize verified work for <window and scope>. Separate proposed, approved, attempted, verified-complete, failed and uncertain actions. List unresolved decisions, actual owners, due dates, source links and next steps. Reconcile draft counts against the current draft manifest. Preserve coverage gaps and independent checkpoints. Do not report a generated summary as a completed interaction or claim business impact without evidence.

