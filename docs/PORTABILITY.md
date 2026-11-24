# Portability and adoption

## What is portable

Plain-text instructions, documented data contracts, and local program files can be inspected by many coding assistants. The core should not depend on a particular chat provider to express its workflow rules.

## What is not automatic

Reading a README does not install a connector or create execution access. An assistant needs a compatible runtime, filesystem access, tool permissions, and any required dependencies. A text-only chat can explain the package but cannot run it. Different providers interpret instructions and expose tools differently; no cross-provider certification is implied.

Production workspaces also differ in identifiers, pagination, timestamps, permissions, custom-field schemas, and write semantics. A generic demonstration is a starting point for adaptation, not a drop-in integration for every CS team.

## Adoption sequence

1. Run the offline example unchanged and inspect its output.
2. Map the team's approved workflow to the package's concepts. Identify gaps rather than changing policies implicitly.
3. Implement a read-only adapter against a sandbox workspace. Validate identity, complete pagination, timezone handling, errors, and source links.
4. Produce reviewable proposals from sandbox evidence. Test conflicting values, ambiguous matches, missing pages, stale data, and duplicates.
5. Implement a separate write adapter with explicit authorization, durable audit state, readback, concurrency protection, and uncertain-outcome handling.
6. Run a small approved pilot and reconcile every outcome. Expand only after review of failures and coverage.

## Adapter acceptance checklist

- Which operations are read-only, and which mutate external state?
- Which fields, projects and workspaces can the integration access?
- How are real user approval and exact action scope authenticated?
- Can source records be linked to the evidence behind each proposal?
- Does a partial read block conclusions that require complete coverage?
- Are retries safe across restarts and concurrent workers?
- How are existing values, changed evidence, and stale proposals handled?
- Can an uncertain response be reconciled without repeating the action?
- Are logs redacted and retained under an approved policy?
- Which environments and assistant providers were actually tested?

Keep a separate verification record for each adapter and provider. A successful offline test is not evidence of a successful production connection.

