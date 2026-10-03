---
document_id: accounts_currencies_exchange_v1
title: Supported Currencies and Currency Exchange
route: account_currency_and_access
topic: currencies_and_exchange
country: global
effective_date: 2026-10-01
version: 1.0
source: Synthetic Bank Currency and Exchange Guide
---

# Supported Currencies and Currency Exchange

Use the supported-currencies tool for the current list of currencies and the
exchange-rate tool for a current currency pair. This document explains general
behavior and must not be used as a live rate quote.

## Standard supported currencies

The standard synthetic-bank currency set is:

| Code | Currency | Standard decimal places |
| --- | --- | ---: |
| EGP | Egyptian Pound | 2 |
| USD | US Dollar | 2 |
| JOD | Jordanian Dinar | 3 |
| EUR | Euro | 2 |
| GBP | British Pound | 2 |

Whether a currency can currently be held, exchanged, transferred, or used for
a particular product must be confirmed through the relevant authorized tool.

## Exchange rates

An exchange rate states how much of the quote currency equals one unit of the
base currency. Rates can change and can expire. Always identify the base and
quote currency explicitly before checking a rate.

Do not derive the reverse direction by mental calculation and do not reuse a
rate from an earlier transaction. Request the exact direction from the current
exchange-rate tool.

## Exchanging in the application

Before confirmation, the authenticated application should show:

- The source currency and amount.
- The destination currency and estimated amount.
- The applicable exchange rate.
- Any bank fee known at confirmation time.

The displayed confirmation screen takes priority over general examples. The
rate may change until the customer confirms. Third-party providers, merchants,
cash machines, and intermediary banks may use their own rates or fees.

## Availability and restrictions

Currency availability can depend on country, account type, verification status,
market availability, and regulatory restrictions. A supported currency is not
a guarantee that every customer can open an account in it or use every transfer
method.

Support must not promise a future rate, investment outcome, or guaranteed
saving from exchanging at a particular time.

## Failed or missing exchanges

For a failed exchange, the customer should check the application message and
their source and destination balances. If one balance was debited without the
other being credited, stop repeated attempts and escalate through an
authenticated support channel with the transaction reference.
