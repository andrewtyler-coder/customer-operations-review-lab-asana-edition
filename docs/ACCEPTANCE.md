# Acceptance checklist: validating the workflow before trusting it

This checklist shows how a human validates a run of this synthetic workflow
before relying on its output. It is a demonstration artifact: generic gates
for human oversight of an AI-assisted CS workflow, not a certification of
any live system. Every row starts NOT RUN; a missing capability is BLOCKED,
not passed, and an unchecked source is UNREVIEWED, not assumed fine.

| Gate | Test | Pass condition | Hold condition |
| --- | --- | --- | --- |
| 1. Scope | Confirm the book of business and read-only intent for the run. | Accounts and scope are explicit. | Wrong roster, inherited assumptions, or unclear scope. |
| 2. Coverage | Compare the daily brief against the full account list. | Every account has an action or a named gap. | Any account silently absent; "nothing new" on incomplete reads. |
| 3. Evidence | Spot-check that each proposal cites exact account/field/period evidence. | Evidence IDs match their source records. | Inferred, fuzzy, or missing evidence treated as sufficient. |
| 4. Exceptions | Inspect the exception queue. | Missing, ambiguous and conflicting evidence is escalated, not resolved by guessing. | Any exception auto-resolved or dropped. |
| 5. Approvals | Verify each applied change traces to an exact approved payload. | Approval binds to the exact change; stale approvals die after an uncertain attempt. | A changed or unapproved payload applied; a retry after uncertainty without reconciliation. |
| 6. Read-back | Compare each applied change with what actually saved. | Saved state matches the approved payload. | Apply reported without verification; mismatch treated as success. |
| 7. Follow-up ladder | Review cadence output for a sample of accounts. | First trigger and repeat entries are distinguished; a verified response closes the cycle; an exhausted ladder escalates. | Unverified touches counted; outreach continuing after a verified reply. |
| 8. Open loops | Review the carryover queue. | Pending approvals, promised follow-ups and missing items carry with owner and due date. | A loop closed without verified completion, or dropped silently. |
| 9. Closeout | Verify the end-of-day record against what saved. | Submit once, verify saved state. | Resubmission on rendering doubt; duplicate closeout. |
| 10. Boundaries | Confirm nothing external happened. | No sends, posts, shares or record writes outside the approved mock step. | Any unapproved external effect. |

## Using this checklist

Run it per demonstration session. A gate that cannot be checked stays open
and names what is missing. The point is the posture: an AI teammate prepares
and proposes; people approve exact changes, verify saved results and own
every consequential decision.

