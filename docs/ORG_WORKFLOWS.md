# How Asana's CS org maps to this workflow model

Compiled from public sources on November 14, 2026 (leadership pages, job postings, a CCO podcast write-up, and a Sales Navigator title export). This is a broad map from self-reported titles, not a verified census or org chart; functional groupings are not reporting lines. It exists so the prototype's concepts can be discussed in the vocabulary the real team uses. Nothing here is internal information.

## The functions and their daily work

- **Portfolio / Scaled Customer Success Managers.** Time-bound engagements across a broad book; risk of accounts going quiet between touches. Maps to `operations.portfolio_health` (blank health stays unknown, stale reviews surface) and `operations.task_attention` (baseline comparison instead of re-surfacing old overdue items).
- **Named / Top / Strategic Accounts CSMs.** Fewer, deeper relationships; business reviews on outcomes. Maps to `operations.account_review_prep` (evidence-linked briefing, known facts separated from open questions) and `operations.engagement_proposals` (commitments proposed only from explicit, human-labeled statements).
- **At-Risk Renewals program (under the CCO).** Flags enterprise renewals 9-12 months out from utilization, a data-science retention score, qualitative signals and support-ticket patterns; every new flag gets a bi-weekly human review; forecast standard is tight. Maps to `operations.signal_triage` (four signal families, thresholds as configuration, missing data escalates) plus the operating playbook's review cadence. The doctrine the code encodes - a flag is a reason to review, low utilization is a symptom not a verdict - comes from this program's public description.
- **Renewals managers (AMER East/West, EMEA, APAC).** Commercial execution on flagged and unflagged renewals. Maps to the exception queue in `workflow.py` (conflicting or missing evidence held for a human) and to the handoff boundaries in `system.CSWorkspaceCycle` (unresolved decisions carry forward with owners).
- **AI Adoption function / AI Success Architects.** Owns post-sales AI adoption, consumption and 30/60/90 benchmarks for enterprise accounts, and diagnoses which customer workflows should become AI Studio rules, AI Teammates or MCP integrations. Maps to `operations.adoption_benchmarks` (missing usage data escalates rather than marking an account behind) and `operations.capability_map` (candidate mappings a human validates).
- **Customer Product Support.** Global intake with AI-assisted deflection; Asana's own published pattern routes questions into a triage project, lets AI answer from known resources, and escalates the rest to humans with explicit owners and SLAs. Maps to `operations.intake_coverage` (complete-window, deduplicated intake; partial reads block advancement) and the playbook's escalation rules.
- **Customer Education / Enablement.** Champions programs and content. Maps to `operations.handoff_manifest` (drafts recomputed from current content, never auto-published) and the playbook's adoption-tracking section.

## What this means for the prototype

The demo's synthetic day - intake coverage, signal triage, account prep, approval-gated field updates, EOD handoff - is one loop that touches every function above. The honest framing stays: thresholds, cadences and mappings are caller configuration, the helpers process supplied records only, and none of this is connected to a live workspace.

## Sources

- CCO appointment and scope: https://investors.asana.com/news-releases/news-release-details/asana-appoints-josh-abdulla-head-customer-experience
- CX reshaping with Portfolio Success Managers and At-Risk Renewals (CCO anniversary post, Sept 2025): https://www.linkedin.com/posts/josh-abdulla-333297_this-week-marks-my-one-year-anniversary-at-activity-7373543968099205120-YUhs
- Red Renewals process detail (Nov 2026): https://amplifyam.com/resources/josh-abdulla-red-renewals-asana
- AI Success Architect role scope: https://www.asana.com/jobs/apply/8349347
- Slack + AI Studio support intake pattern: https://asana.com/resources/slack-asana-integration-ai-studio-product-support

