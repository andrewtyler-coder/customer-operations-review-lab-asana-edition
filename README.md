# Customer Operations Review Lab: Asana Edition

**A synthetic, offline customer-success operations cycle modeled on Asana concepts: an AI Teammate that drafts account updates, an exception queue that escalates to humans, approval-gated changes, and end-of-day handoff narratives.** This is a new portfolio starter, not an export of an employer's system, not an Asana integration, and not affiliated with or endorsed by Asana. No real customer data, company source code, credentials, workspace exports or Git history are included.

## Why it exists

Customer success teams running their book of business in Asana face a specific question: where can an AI Teammate actually help, and where must a human stay in the loop? Filling a blank health field is easy; knowing when the evidence is sufficient, when to escalate to a human, and how to leave an accountable review trail is harder. This small project demonstrates those decisions on Asana-shaped records (tasks, custom fields, sections, stories, form intake) without connecting to Asana, its API, or its MCP server.

The design follows Asana's own published framing: AI Studio handles high-volume repeatable work, AI Teammates handle context-and-judgment work with checkpoints, and certain actions always require human approval. It also borrows from how Asana's own customer success leadership describes renewal-risk management: flag risk early from multiple signals, review every flag with a human, and treat low utilization as a symptom to investigate, not a verdict.

## Run it

Requires Python 3.10+; standard library only. From this directory:

```sh
python3 workflow.py
python3 demo_operations.py
python3 demo_system.py
python3 demo_followthrough.py
python3 -m unittest discover -s tests -v
```

The commands print proposed changes, exception queues and review material. They do **not** apply changes or connect to anything. The tests exercise in-memory mock apply operations, never a live workspace.

Expected demonstration: one proposed custom-field update, one account with no evidence, and one account with conflicting evidence. A repeated imported evidence record does not create a second proposal.

## What it demonstrates

- Portfolio health rollup across a book of accounts, where blank health stays unknown instead of being assumed healthy, and accounts without a recent verified review are surfaced as unreviewed.
- Renewal-risk signal triage (utilization, retention score, qualitative changes, support engagement) that flags accounts for human review and escalates missing or contradictory signal data instead of inferring it.
- Workflow-to-capability mapping: a described manual workflow is proposed as an AI Studio rule, an AI Teammate, an MCP integration or manual work, always as a candidate a human validates.
- AI adoption tracking against 30/60/90-day benchmarks, where missing usage data escalates rather than marking an account behind.
- Exact account/field/period evidence matching, deliberately conservative rather than fuzzy.
- Repeated identical evidence deduplication by stable record identity.
- Missing evidence stays blank, not interpreted as proof that an account is fine.
- Ambiguous evidence and existing-value conflicts held in a human-owned exception queue.
- Approval tied to the exact proposal payload, stale-value checks before mock application, idempotent mock application and a local audit record.
- Follow-up cadence tracking that counts only verified outreach, distinguishes a first trigger from repeat follow-up, shows the exact step still owed, escalates an exhausted ladder to a human and stops on a verified response; status changes are proposals for human approval, never automatic.
- Coverage-accounted daily briefs where every account gets an action or an explicitly named gap, and incomplete reads can never be summarized as "nothing new."
- An approval-bound action protocol: one exact payload approved once, applied once, read back after saving, and any uncertain outcome reconciled by a human before any retry.
- Evidence resolution by exact ID from a primary source with a documented, labeled fallback, where an internal reference never substitutes for a required shareable link and incomplete reads forbid calling anything the latest record.
- An open-loop carryover queue that keeps pending approvals, promised follow-ups and missing items visible with owner and due date until verified completion.
- Submit-once closeout verification: the saved record is checked before a closeout counts, and resubmission on doubt is blocked as a duplicate risk.
- End-of-day handoff narratives (comment and status-update drafts) that are recomputed from current drafts and never auto-posted.

## Portfolio positioning

Present this as an **AI-assisted CS operations workflow prototype** demonstrating process design, exception handling, human-in-the-loop controls and review boundaries on Asana concepts. Describe your own contribution accurately. This starter was AI-generated; it is not evidence of independently authored production software, measured time savings, customer impact, enterprise deployment, or any relationship with Asana. Add independently verified experience separately, only if you have permission to disclose it.

Suggested truthful headline: "Customer operations workflow design on Asana concepts: AI-teammate proposals, exception queues and approval-gated updates."

See [case study template](docs/CASE_STUDY.md), [architecture and limitations](docs/ARCHITECTURE.md), [agent onboarding](docs/AGENT_GUIDE.md), [acceptance checklist](docs/ACCEPTANCE.md) and [publication checklist](docs/PUBLISHING.md).

## Current boundaries

No Asana API, MCP server, OAuth, webhooks, LLM calls, persistent storage, concurrency support or real notifications. The approval method is a test interface, **not** secure human authentication. Audit records are in memory and not tamper-resistant. The capability mapping is a rules-of-thumb proposal, not a purchasing or architecture recommendation. No production-readiness or legal clearance is claimed. No open-source license has been selected; decide ownership and licensing before public distribution.

## Cold start and expansion

Read [AGENTS.md](AGENTS.md) for a new assistant's operating boundaries, [portability](docs/PORTABILITY.md) for adaptation requirements, [data contracts](docs/CONTRACTS.md) for the local fixture shape, and [workflow roadmap](docs/WORKFLOW_ROADMAP.md) for an explicit working-versus-planned capability map. A real deployment would reach Asana through its MCP server or REST API behind organization-approved authentication, authorization and audit controls; none of that exists here.

## Full local cycle and operating guides

`system.CSWorkspaceCycle` coordinates supplied intake coverage and task coverage, account review preparation, explicit caller-attested mock check-ins, post-engagement proposals, current-draft review and end-of-day handoff. It preserves unresolved decisions and exposes incomplete coverage. This is an executable **offline system demonstration**, not a live Asana integration or automated customer communication.

- [Operating playbook](docs/OPERATING_PLAYBOOK.md): book-of-business configuration, start-of-day, account review preparation, post-engagement work, field updates and EOD/EOW.
- [Agent task templates](docs/AGENT_TEMPLATES.md): cold-start and workflow-specific instructions.
- [Capability map](docs/WORKFLOW_ROADMAP.md): implemented components versus required production work.
- [Source safety](docs/SOURCE_SAFETY.md): untrusted evidence, privacy and adapter boundaries.
- [Org workflow map](docs/ORG_WORKFLOWS.md): how Asana's publicly described CS functions (Portfolio CSMs, At-Risk Renewals, AI Adoption, Support, Education) map to this prototype's components.
- [Demo captures](docs/demo-captures/): real terminal output from the three demo entry points, captured November 16, 2026.

Meeting statements are human-labeled inputs, not AI transcript extraction. Mock check-ins require an evidence ID but are not independently verified. No real Asana records are read or updated by these demonstrations.

