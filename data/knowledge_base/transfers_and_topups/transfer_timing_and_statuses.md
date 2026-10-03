---
document_id: transfers_timing_statuses_v1
title: Transfer Timing and Status Guide
route: transfers_and_topups
topic: transfer_timing_and_statuses
country: global
effective_date: 2026-10-01
version: 1.0
source: Synthetic Bank Operations Manual
---

# Transfer Timing and Status Guide

This policy explains the normal processing times and customer-visible statuses
for bank transfers. Actual transfer details must always be checked with the
customer's transfer-status tool before giving an account-specific answer.

## Transfer statuses

### Pending

A pending transfer has been created but has not reached the recipient's bank.
Pending transfers are normally reviewed or processed within two hours. A
transfer can remain pending for up to one business day when it requires routine
security checks, beneficiary verification, or processing by a banking partner.

A pending outgoing transfer may be cancelled if the cancellation tool confirms
that cancellation is still available. The customer must explicitly confirm the
request before cancellation. Do not promise that a transfer was cancelled
until the tool reports a successful result.

### Completed

A completed transfer has been sent successfully. Transfers between accounts at
the bank usually arrive within a few minutes. Domestic transfers to another
bank usually arrive on the same business day when submitted before 14:00 local
time, or by the next business day when submitted later.

International transfers normally take two to five business days. Weekends,
public holidays, intermediary banks, and recipient-bank reviews may extend the
delivery time.

A completed transfer cannot be cancelled through the application. If the
recipient has not received it after the expected delivery window, support can
start a transfer trace. A trace investigates delivery and does not guarantee a
reversal.

### Failed

A failed transfer was not sent. Common causes include unavailable banking
partners, invalid recipient-bank details, technical problems, or an account
restriction. Money reserved for a failed transfer is normally released to the
available balance immediately, but it may take up to one business day.

The customer should verify the beneficiary details before trying again. Do not
advise repeated attempts when the failure reason indicates an account or
security restriction.

### Declined

A declined transfer was rejected before it was sent. Possible reasons include
insufficient available balance, an unverified or blocked beneficiary, a limit
being exceeded, or a required security check not being completed.

The customer should follow the specific failure reason shown by the transfer
tool. Bank security rules or verification requirements must not be bypassed.

### Cancelled

A cancelled transfer will not be sent. Reserved funds are normally returned to
the available balance immediately, although the displayed balance can take a
few minutes to refresh. A cancelled transfer cannot be restarted; the customer
must create a new transfer if they still want to send the money.

## Missing incoming transfers

Before investigating a missing incoming transfer, confirm that the expected
delivery window has passed. Ask the sender to verify the recipient details and
provide the sending bank's transfer reference. Incoming transfers that are
still within the normal processing window should not be reported as failed.

## Business days and cutoff times

Business days exclude weekends and public holidays in any country involved in
the transfer. The domestic-transfer cutoff time is 14:00 in the account's local
time zone. Transfers submitted after the cutoff are treated as submitted on the
next business day.

## Escalation

Escalate to transfer support when:

- A domestic transfer is not delivered after two business days.
- An international transfer is not delivered after five business days.
- A failed or cancelled transfer has not released reserved funds after one
  business day.
- The transfer status and the displayed balance appear inconsistent.
- The customer does not recognize the transfer.

An unrecognized transfer is a security concern. Do not tell the customer to
contact the recipient directly. Advise them to secure their account and contact
bank support through an authenticated channel.
