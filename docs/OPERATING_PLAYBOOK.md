# Configurable customer-success operating playbook (Asana edition)

This is a fresh, company-neutral operating specification for a CS team running its book of business in Asana. It is not a released employer SOP and not Asana documentation. Local helpers demonstrate parts of the process with synthetic inputs; external execution requires authorized adapters and organization-specific configuration. The written procedure is broader than the code.

## Book-of-business configuration checklist

Before a live pilot, an authorized owner must define:

- Account identity key, current ownership field, active scope and included lifecycle stages (a CSM's portfolio is roughly 50 enterprise accounts; the code takes the roster as supplied).
- Asana projects, sections and custom fields used for intake, account reviews, exceptions and handoffs, with source-of-truth precedence for each field.
- Renewal-risk signals and thresholds: utilization floor, retention-score source, qualitative signal categories, support-engagement ceiling. Low utilization is a symptom to investigate, not a verdict.
- Adoption plan: 30/60/90-day benchmarks per account and what counts as an active AI workflow.
- Local reporting timezone, business hours and coverage windows. Store event timestamps with offsets; display the configured timezone.
- Allowed read scopes, allowed write fields, permitted audiences and approval boundaries: which actions an AI Teammate may draft, which it may never take, and which always require a named human.
- What qualifies as a commitment, a completed check-in, an escalation and a verified task completion.
- Due-date rules, urgency thresholds, reporting recipients and quiet/no-change behavior.
- Retention, deletion, secret storage and audit policies.

Leave unspecified settings unresolved. Do not invent credentials, policy, recipients, identity mappings or permissions. A configuration checklist is not automatically loaded by this demonstration.

## Start of day (SOD)

**Inputs:** current book of business; last verified intake checkpoint; submission deduplication IDs; independent task baseline; unresolved decisions; configured cutoff.

1. Freeze a timezone-aware cutoff. Resolve the complete current book across configured stages, not merely records authored by the operator.
2. Retrieve every page from each permitted source. Record failures and incomplete pages. Use overlap retrieval when needed, then locally apply the exact coverage window.
3. Review intake once per stable GID, preserving the original submission text separately from any summary. Flag contradictory versions rather than silently selecting one.
4. Compare tasks with their own baseline. Report actual assignees, newly relevant tasks, meaningful changes and newly due items. Do not repeatedly surface unchanged old overdue items as new.
5. Keep missing tasks unresolved until a source verifies completion, deletion or changed scope.
6. Run renewal-signal triage: flag accounts for review from the configured signals, and escalate missing or contradictory signal data. A flag is a reason to review, never an automated account change.
7. Combine findings into priorities: time-sensitive attention, decisions waiting on the operator, planned account reviews and unresolved coverage gaps.
8. Advance each checkpoint only for its verified coverage. Do not let a successful intake read hide a failed task read.

**Review output:** account; source link; type; event time/due date; factual detail; assignee; suggested next action; coverage state. No outgoing messages or live writes occur merely because the report exists.

**Code support:** `operations.intake_coverage`, `operations.signal_triage` and `operations.task_attention` process supplied local inputs. They do not fetch pages, discover ownership, persist state or deliver notifications.

## Portfolio health review

1. Roll up the supplied account tasks by health value. Blank health is unknown, not healthy; report it separately.
2. Surface accounts with no verified review inside the configured window. A missing review is a gap, not a clean bill.
3. Keep counts scoped to supplied records; never extrapolate to the whole book.

**Code support:** `operations.portfolio_health` computes counts and unreviewed lists from supplied rows. It does not read a live portfolio.

## Account review preparation

1. Verify the intended account and meeting from authorized sources.
2. Assemble recent source-linked stories, open tasks and unresolved decisions. State the age and completeness of the evidence.
3. Separate known facts from proposed agenda questions. Do not invent sentiment, promises or account health.
4. Highlight changes since the last verified interaction and matters requiring a human decision.
5. Leave check-in status unchanged. Preparing a briefing is not evidence that a review occurred.

**Output:** purpose; known facts and links; open commitments with actual owners/dates; unresolved decisions; agenda; unknowns.

**Code support:** `operations.account_review_prep` selects up to five latest supplied stories, supplied open tasks and unresolved decisions. It does not read a calendar, transcribe a call or verify meeting completion.

## Post-engagement administration

1. Confirm the evidence belongs to the correct account and interaction. Obtain authorized transcript or notes access before reading.
2. Separate explicit commitments from suggestions, questions and incomplete statements. Preserve evidence references.
3. Propose tasks only with explicit action and owner. Preserve a missing due date as unknown, not a guessed deadline.
4. Propose custom-field updates separately, showing current value, proposed value and supporting source. Hold conflicting or stale values in the exception queue.
5. Prepare any comment or status update as a draft. Show exact destination and text for review where required.
6. Obtain scoped approval, execute only the approved actions through a validated adapter, and verify results. Record partial or uncertain outcomes individually.
7. Keep unresolved decisions in the handoff. Do not silently mark check-ins or tasks complete based on a generated recap.

**Code support:** `operations.engagement_proposals` accepts already human-labeled statements. It is not an LLM extraction or transcription system and performs no writes.

## AI capability planning

1. Describe each manual workflow: volume, structure (repeatable versus judgment), and external systems involved.
2. Map candidates conservatively: high-volume repeatable work inside Asana to an AI Studio rule; context-and-judgment work to an AI Teammate with checkpoints; cross-system work to an MCP integration; anything incompletely described stays manual until a human scopes it.
3. Treat every mapping as a candidate. A human validates fit, cost, data access and governance before anything is built or enabled.

**Code support:** `operations.capability_map` produces candidate mappings only. It builds nothing and changes nothing.

## Adoption tracking

1. Agree 30/60/90-day benchmarks per account before measuring. Benchmarks measure adoption, not business outcomes.
2. Compare supplied usage rows against the plan. Report on track or behind per checkpoint with actual numbers.
3. Escalate missing usage data. An account is never marked behind on absent data.
4. Package results for business reviews focused on outcomes and value, with the underlying evidence attached.

**Code support:** `operations.adoption_benchmarks` compares supplied rows to a caller-supplied plan. It does not fetch usage data.

## Handoff review

1. Build comment and status-update drafts from verified facts and the approved communication purpose.
2. Check exact account, destination project/task, and text. Show unresolved questions before asking for approval.
3. Recompute the review manifest and count from the exact current drafts, including additions, removals and revisions.
4. Approval of old content does not approve revised text, a new destination or an added draft.
5. Before posting, recheck authorization and current state. After an uncertain response, reconcile before retrying.

**Code support:** `operations.handoff_manifest` produces a count and content hash. It does not authenticate approval, post anything, persist drafts or reconcile delivery.

## Evidence-backed field updates

1. Match account, field and period using explicit identifiers and documented mappings.
2. Deduplicate repeated identical evidence. Hold absent or contradictory evidence in the exception queue.
3. Preserve existing values unless an exact, authorized replacement is reviewed. Absence of evidence is not proof that an account is fine.
4. Show exact proposed changes and bind review to that payload.
5. Recheck destination state immediately before execution. Record and verify the outcome.

**Code support:** `workflow.py` demonstrates conservative exact matching and in-memory mock approval/application. Real authorization, durable state and external writes are not implemented.

## End of day / week (EOD/EOW)

**Code support:** `system.CSWorkspaceCycle.end_day` aggregates local coverage, caller-attested mock check-ins, unresolved decisions, engagement proposals, current draft manifest and mock audit. This is not a live daily report. Weekly aggregation, scheduled delivery and durable handoffs remain integration work.

- Summarize verified activity covered, actions actually completed, pending drafts/proposals, unresolved decisions, due commitments and coverage gaps.
- Label items as proposed, approved, attempted, verified completed, failed or uncertain. Never collapse these states into "done."
- Carry unresolved work forward with owner, source reference and next step.
- Include only evidence-backed counts. Report a changed draft count from the current manifest, not an earlier message.
- Preserve separate intake/task checkpoints and their completeness. Produce no-change reports only if the team wants them.
- Weekly reporting may aggregate verified daily results, but must not invent business outcomes or time saved.

## Escalation and recovery

Stop the affected action on ambiguous identity, conflicting evidence, incomplete reads, stale approval, changed destination, unavailable permissions or uncertain writes. Continue independent read-only work when useful. Report what was attempted, what is verified, what remains unknown and the smallest decision or access requirement needed. Never expand workspace permissions as an automatic recovery step.

## Running the complete local cycle

Run `python3 demo_system.py` from the repository root. `system.CSWorkspaceCycle` joins the local stages: start-day coverage, account review preparation, explicit evidence-ID-based mock check-in recording, post-engagement proposals, draft review and end-day handoff. It rejects an end-day report before a start-day check and propagates incomplete coverage. `record_check_in` records a caller attestation, not independently verified real completion. A real deployment must authenticate and verify that evidence. All state remains in memory; nothing is posted or written externally.

