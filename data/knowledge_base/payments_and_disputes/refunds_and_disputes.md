---
document_id: payments_refunds_disputes_v1
title: Refund and Payment Dispute Process
route: payments_and_disputes
topic: refunds_and_disputes
country: global
effective_date: 2026-10-01
version: 1.0
source: Synthetic Bank Refund and Dispute Policy
---

# Refund and Payment Dispute Process

Refunds and disputes are different processes. Inspect the original transaction
and any existing refund or dispute before describing its status. Creating or
cancelling a request changes customer data and requires explicit confirmation.

## Refunds

A refund returns money from a completed transaction. A full or partial refund
can be requested only against a completed transaction, and total active refund
requests cannot exceed the original amount.

Refund statuses are:

- **Requested:** The request was created and awaits processing.
- **Processing:** The refund was accepted and is moving through payment rails.
- **Completed:** The refund was credited successfully.
- **Declined:** The refund request was not approved or could not be processed.

Once a merchant or bank refund is processing, it normally reaches the account
within five to ten business days. The exact expected date from the refund-status
tool takes priority over this general window.

## Disputes

A dispute asks the bank to investigate a transaction. It can be appropriate for
an unrecognized payment, duplicate completed charge, cash-machine discrepancy,
or a merchant issue that could not be resolved directly.

Dispute statuses are:

- **Submitted:** The dispute was received.
- **Under review:** The bank is investigating.
- **Awaiting customer:** More information is required from the customer.
- **Resolved:** The investigation finished with a recorded resolution.
- **Rejected:** The dispute did not qualify or the evidence did not support it.
- **Cancelled:** The customer cancelled it before final resolution.

An unresolved dispute can be cancelled after explicit customer confirmation.
A resolved or rejected dispute cannot be cancelled. Only one active dispute can
exist for the same transaction.

## Evidence and safety

The customer may be asked for receipts, merchant correspondence, cancellation
evidence, or a description of what happened. Evidence must be submitted only
through a secure authenticated channel. Never request passwords, PINs, CVVs,
full card numbers, or authentication codes.

Do not promise provisional credit, reimbursement, a decision date, or a
successful outcome unless an authorized tool or case record confirms it.

## Urgent unrecognized payments

For an unrecognized card payment or withdrawal, help the customer secure the
card first, inspect the transaction, and then explain the dispute process. A
dispute alone does not block the card or secure a compromised account.
