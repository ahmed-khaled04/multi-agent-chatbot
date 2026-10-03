---
document_id: cards_lifecycle_delivery_v1
title: Card Types, Activation, Delivery, and Expiration
route: card_services
topic: card_lifecycle_and_delivery
country: global
effective_date: 2026-10-01
version: 1.0
source: Synthetic Bank Card Services Guide
---

# Card Types, Activation, Delivery, and Expiration

This guide covers physical, virtual, and disposable cards. For the status,
delivery stage, form, or expiry date of a specific card, use the customer's
card-status tool before answering.

## Card types

### Physical cards

Physical debit and credit cards can be used at supported merchants and cash
machines. A newly issued physical card remains inactive until the customer
completes activation through the authenticated bank application.

### Virtual cards

Virtual cards are available in the authenticated application when the
customer's account and region support them. They have card details and an
expiry date but no physical delivery. They can be used for supported online
payments and eligible digital wallets.

### Disposable virtual cards

A disposable virtual card can replace its payment details after an eligible
online purchase. It is intended for one-time online use and may not work for
subscriptions, deposits, offline terminals, cash withdrawals, or merchants
that charge the card later.

## Physical-card delivery stages

- **Ordered:** The request was accepted but the card has not shipped.
- **Shipped:** The card was handed to the delivery provider.
- **Delivered:** Delivery was recorded as complete.
- **Returned:** The delivery provider returned the card to the bank.
- **Not applicable:** The card is virtual or disposable and has no delivery.

Standard physical-card delivery normally takes five to ten business days.
Remote areas, public holidays, address problems, and customs checks can extend
delivery. Do not promise a delivery date that is not shown by an authorized
tracking channel.

## Activation

The customer should activate a delivered physical card in the authenticated
application. Activation may require confirmation of masked card details and a
secure authentication step. Support must never ask for the full card number,
PIN, CVV, passcode, or one-time authentication code.

An inactive card cannot be activated by chat. If activation fails, confirm the
card status and direct the customer to the application's card controls or an
authenticated support channel.

## Expiration and replacement

A card remains valid through the final calendar day of its printed expiry
month unless it has already been blocked or closed. Eligible replacement cards
are normally issued before expiration. Delivery availability and timing depend
on the customer's current address and country.

An expired card cannot be reactivated. Recurring merchants and digital wallets
may need the replacement card details after issuance.

## Escalation

Escalate to card support when:

- A physical card has not arrived ten business days after shipment.
- Delivery is marked completed but the customer did not receive the card.
- A returned card needs a corrected delivery address.
- Activation fails after the application confirms the card was delivered.
- An expected replacement has not been issued near the expiry date.
