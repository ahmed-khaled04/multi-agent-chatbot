---
document_id: topups_methods_limits_verification_v1
title: Top-Up Methods, Limits, and Verification
route: transfers_and_topups
topic: topup_methods_limits_and_verification
country: global
effective_date: 2026-10-01
version: 1.0
source: Synthetic Bank Top-Up Policy
---

# Top-Up Methods, Limits, and Verification

This policy covers adding money to a bank account. For a specific top-up, use
the top-up-status tool before describing whether it is pending, completed,
failed, reversed, or awaiting verification.

## Supported top-up methods

### Debit or credit card

The bank accepts supported personal debit and credit cards in the cardholder's
name. Prepaid, anonymous, commercial, and third-party cards may be rejected.
The card issuer may apply its own cash-advance or foreign-transaction fee.

Card top-ups normally appear within a few minutes. The customer may be asked to
complete 3-D Secure or another issuer verification step.

### Bank transfer

Customers can add money by transferring funds to their bank-account details.
The sender name should match the customer's verified name. Domestic bank
transfers normally arrive on the same or next business day. International bank
transfers normally take two to five business days.

### Cash and cheque

Cash and cheque top-ups are available only through supported partner locations.
Availability depends on the customer's country. Cash and cheque deposits may
remain pending until the source of funds and the deposit are verified. Cheques
normally require three to seven business days to clear.

## Standard top-up limits

The standard limits for a verified personal account are:

| Method | Maximum per top-up | Maximum per day |
| --- | ---: | ---: |
| Card | 2,000 USD equivalent | 5,000 USD equivalent |
| Bank transfer | 10,000 USD equivalent | 25,000 USD equivalent |
| Cash | 1,000 USD equivalent | 2,000 USD equivalent |
| Cheque | 5,000 USD equivalent | 10,000 USD equivalent |

The bank converts these limits into the account currency using its current rate.
Lower limits can apply to new accounts, accounts with incomplete verification,
or accounts under review.

## Top-up statuses

### Pending

The top-up has been received but is still processing. Card top-ups normally
resolve within two hours. Bank-transfer, cash, and cheque top-ups follow their
method-specific delivery times.

### Completed

The money was credited successfully and is included in the account balance.

### Failed

The top-up was not credited. Common reasons include issuer rejection,
unsupported source, invalid sender information, an exceeded limit, or failed
authentication. The customer should follow the failure reason returned by the
top-up tool.

### Reversed

A previously credited or authorized top-up was returned to its source. Card
reversals normally appear at the source bank within five to ten business days.
The exact timing is controlled by the card issuer.

### Verification required

The top-up is paused until the requested identity or source-of-funds evidence is
reviewed. The customer should upload documents only through the bank's secure,
authenticated channel. Documents must not be sent through chat.

## When verification may be required

Verification may be requested when:

- The source name does not match the customer's verified name.
- A top-up is unusually large or differs from normal activity.
- Several cards or funding sources are used in a short period.
- A cash or cheque deposit requires proof of origin.
- Identity verification is incomplete or outdated.

Support cannot bypass verification or guarantee approval. Once the requested
documents are received, review normally takes one to three business days.

## Fees

The bank does not charge for domestic bank-transfer top-ups. A card top-up may
include a fee of up to 1% when the source card uses a different currency. Cash,
cheque, intermediary-bank, and card-issuer fees are shown when known but may be
charged separately by the provider.

## Escalation

Escalate to top-up support when:

- A card top-up remains pending for more than two hours.
- A bank-transfer top-up is missing after two business days.
- A cheque top-up is pending after seven business days.
- A reversal has not returned to the source after ten business days.
- The customer does not recognize the funding source.
