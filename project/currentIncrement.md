# Current increment

## Increment

Money Movements and Payment Arrangements.

## Branch

`feature/banking-core`

## Objective

Represent how money is expected to move, and how obligations are paid, without
collapsing the bill, the payment instruction, the expected flow and statement
evidence into one record.

## Scope

- `Obligation` — what has to be paid or maintained.
- `PaymentArrangement` — Direct Debit, standing order and related instructions.
- `MoneyMovement` — expected inflow or outflow.
- `TransactionObservation` — dated evidence that a movement occurred.
- Cancelling an arrangement does not end the obligation.
- Optional banking capture fields can create these typed records.
- Persistence through the shared `RecordStore` port.

## Explicit exclusion

Do not implement:

- full transaction history or a ledger;
- Direct Debit or standing-order processing and cancellation workflows;
- bank-statement parsing, OCR or Open Banking;
- payment instruments, banking reports or executor/attorney workflows;
- the full continuity dependency graph.

## Expected exit criteria

- Tests prove the four-record boundary, distinct mechanisms, salary inflow
  without an arrangement, transaction evidence that does not mutate an
  arrangement, persistence, conflicts, secrets rejection, Clann isolation and
  capture.
- Requirement 009 remains in progress.
- `pytest` passes.
- `manageProject --check` reports zero failures and zero warnings.

## Immediate next action

Keep Banking Core on this branch until maintainers merge it, or continue with
statement-import candidates and dependency edges as a later increment.
