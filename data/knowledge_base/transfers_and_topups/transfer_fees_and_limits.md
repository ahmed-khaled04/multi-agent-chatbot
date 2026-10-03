---
document_id: transfers_fees_limits_v1
title: Transfer Fees and Limits
route: transfers_and_topups
topic: transfer_fees_and_limits
country: global
effective_date: 2026-10-01
version: 1.0
source: Synthetic Bank Pricing and Limits Schedule
---

# Transfer Fees and Limits

This document describes the standard synthetic-bank transfer fees and limits.
The application shows the final fee and exchange amount before confirmation.
The displayed confirmation screen takes priority when it differs from this
general schedule.

## Standard outgoing-transfer fees

Transfers between two accounts at the bank are free when no currency conversion
is required.

Standard domestic outgoing-transfer fees are:

| Account currency | Fee per transfer |
| --- | ---: |
| EGP | 5.00 EGP |
| USD | 0.50 USD |
| JOD | Free |
| EUR | 0.50 EUR |
| GBP | 0.50 GBP |

International transfers may include a 5.00 USD equivalent bank fee. Recipient
and intermediary banks may deduct their own charges. Those third-party charges
are outside the bank's control and may reduce the amount received.

The customer must see the applicable bank fee before confirming a transfer. Do
not calculate or promise an account-specific fee without a tool or confirmation
screen.

## Standard transfer limits

The standard limits below apply to verified personal accounts. Lower limits may
apply when identity verification is incomplete, the account is new, or a
security review is active.

| Currency | Maximum per transfer | Maximum per day |
| --- | ---: | ---: |
| EGP | 50,000 EGP | 100,000 EGP |
| USD | 5,000 USD | 10,000 USD |
| JOD | 3,500 JOD | 7,000 JOD |
| EUR | 5,000 EUR | 10,000 EUR |
| GBP | 4,000 GBP | 8,000 GBP |

Incoming transfers do not use the outgoing-transfer limit, but unusually large
incoming transfers may require source-of-funds verification.

## What counts toward the daily limit

Completed and pending outgoing transfers count toward the daily limit.
Cancelled, failed, and declined transfers stop counting after their status is
updated. The daily limit resets at 00:00 in the account's local time zone.

Splitting one transfer into several smaller transfers does not bypass the daily
limit or a verification requirement.

## Currency conversion

When the source account and recipient currency differ, the bank displays the
exchange rate, conversion amount, and any conversion fee before confirmation.
Rates can change until the customer confirms the transfer. Use the authorized
exchange-rate tool for the current synthetic rate; do not infer a rate from an
older transfer.

## Limit increases

Standard limits cannot be increased by a support agent or chatbot. Eligible
customers may request a review through an authenticated support channel. A
review may require completed identity verification and evidence explaining the
source and purpose of the funds. Approval is not guaranteed.

## Security and compliance holds

A transfer within the published limits may still be delayed or declined for a
security, sanctions, identity, or source-of-funds review. Support must not give
instructions for avoiding these checks.
