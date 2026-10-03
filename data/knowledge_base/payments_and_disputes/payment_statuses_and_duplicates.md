---
document_id: payments_statuses_duplicates_v1
title: Card Payment Statuses and Duplicate Charges
route: payments_and_disputes
topic: payment_statuses_and_duplicates
country: global
effective_date: 2026-10-01
version: 1.0
source: Synthetic Bank Payment Operations Guide
---

# Card Payment Statuses and Duplicate Charges

Always inspect the customer's transaction before describing its status. A card
status alone does not prove whether an individual payment completed, failed, or
will be reversed.

## Pending

A pending payment was authorized but has not been finalized by the merchant.
The amount can reduce the available balance while pending. Most pending card
payments resolve within seven calendar days. Hotels, vehicle rentals, fuel
stations, and other deposit-based merchants can hold an authorization for up to
thirty calendar days.

Support cannot manually complete or cancel a pending card payment. If the
merchant cancels the authorization, the available balance updates after the
release reaches the bank.

## Completed

A completed payment was finalized and posted to the account. If the customer
recognizes the payment but wants their money back, they should first ask the
merchant about cancellation or a refund. A completed transaction may be
eligible for a refund request or dispute, but an outcome is not guaranteed.

## Declined

A declined payment was not completed. Common causes include insufficient
available balance, incorrect card details, an inactive or restricted card,
merchant limitations, offline-terminal restrictions, or a security check.

The customer should verify the card status, available balance, merchant details,
and any message shown in the application. Repeated attempts should be avoided
when a security or verification restriction is shown.

## Reversed

A reversed payment was previously authorized but released or returned before
final settlement. The amount normally returns to the available balance
automatically. The merchant might display the original attempt even though the
bank transaction is reversed.

## Duplicate charges

Two similar entries are not necessarily duplicates. One may be pending while
the other is completed, or the merchant may have submitted separate purchases.
Inspect both transactions, including merchant, amount, currency, time, and
status.

If two completed transactions represent one purchase, the customer should ask
the merchant to correct the duplicate. If the merchant cannot help, the
customer may request a dispute after explicitly confirming that action.

## Escalation

Escalate when:

- An ordinary pending card payment remains unresolved after seven days.
- A deposit-based authorization remains after thirty days.
- A reversed payment has not restored the available balance.
- The customer does not recognize a transaction.
- The tool data and displayed balance appear inconsistent.
