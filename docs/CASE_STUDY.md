# Case study template

## Project
Customer Operations Review Lab: Asana Edition (synthetic prototype).

## Problem
CS teams running their book of business in Asana want AI help without losing control: incomplete account records can lead to manual rechecking and accidental overwrites, and renewal risk hides in signals nobody reviews in time. This demo explores a conservative evidence-matching, triage and review workflow on Asana-shaped records.

## My role (complete truthfully)
[Describe requirements, workflow design, review decisions, testing and any implementation you personally performed. State where AI assisted.]

## Decisions demonstrated
Use exact matches; never infer missing facts; blank health is unknown, not healthy; hold conflicts in an exception queue; flag risk for review rather than changing accounts; approve exact changes; check stale records; deduplicate repeated attempts; escalate missing usage data instead of marking accounts behind.

## Evidence
Run the included tests and demonstrations. These validate only the implemented mock behaviors. They do not establish business impact, production reliability, or any connection to Asana.

## Outcomes
Prototype: runnable offline matching, triage, review and mocked update workflow on Asana-shaped records.
Business results: **not measured**. Do not substitute invented savings, percentages, adoption or client counts.

## Next experiment
Use a separately authorized synthetic sandbox to measure review accuracy and exception handling, then gather reviewer feedback. Do not use employer exports or a real customer workspace for a public demo.

## Interview walkthrough
1. Show the missing and conflicting evidence examples in the exception queue.
2. Explain why silence is not proof of absence (blank health, missing usage data).
3. Demonstrate a changed proposal being blocked after approval.
4. Show how a workflow description becomes a candidate AI Studio / AI Teammate / MCP mapping that a human still validates.
5. Explain the gap between this mock and a deployable integration (MCP server, OAuth, durable audit, sandbox pilot).

