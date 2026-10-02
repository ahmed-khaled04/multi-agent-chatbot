"""Create and seed the SQLite database used by the synthetic bank."""

from pathlib import Path
import sqlite3

from src.bank.schema import create_schema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "synthetic" / "bank.db"


CUSTOMERS = [
    (
        "cus_001", "Ahmed Hassan", "ahmed.hassan@example.com", "Egypt",
        "+201001234568", "en", "verified", "2026-09-15T10:30:00Z",
    ),
    (
        "cus_002", "Sara Ibrahim", "sara.ibrahim@example.com", "Egypt",
        "+201112345678", "ar", "verified", None,
    ),
    (
        "cus_003", "Omar Khaled", "omar.khaled@example.com", "Egypt",
        "+201223456789", "en", "pending", "2026-09-29T12:00:00Z",
    ),
    (
        "cus_004", "Layla Nasser", "layla.nasser@example.com", "Jordan",
        "+962790123456", "ar", "verified", "2026-08-21T08:15:00Z",
    ),
    (
        "cus_005", "Youssef Ali", "youssef.ali@example.com", "Egypt",
        "+201334567890", "en", "failed", "2026-09-30T17:45:00Z",
    ),
]


ACCOUNTS = [
    (
        "acc_001", "cus_001", "4821", "checking", "EGP", 250_000,
        40_250, "active", "2025-01-10T09:00:00Z", None,
    ),
    (
        "acc_002", "cus_002", "7319", "checking", "EGP", 82_500,
        82_500, "active", "2025-03-18T11:30:00Z", None,
    ),
    (
        "acc_003", "cus_003", "2056", "savings", "USD", 125_000,
        0, "frozen", "2025-06-02T13:15:00Z", None,
    ),
    (
        "acc_004", "cus_004", "8840", "checking", "JOD", 73_500,
        73_500, "active", "2024-11-22T10:45:00Z", None,
    ),
    (
        "acc_005", "cus_005", "6194", "savings", "EGP", 1_040_000,
        965_000, "active", "2025-08-14T07:30:00Z", None,
    ),
]


SUPPORTED_CURRENCIES = [
    ("EGP", "Egyptian Pound", "E£", 2, 1, 1, 1),
    ("USD", "US Dollar", "$", 2, 1, 1, 1),
    ("JOD", "Jordanian Dinar", "JD", 3, 1, 1, 1),
    ("EUR", "Euro", "€", 2, 1, 1, 1),
    ("GBP", "British Pound", "£", 2, 1, 1, 1),
]


EXCHANGE_RATES = [
    ("USD", "EGP", 48.50, "2026-10-02T00:00:00Z", "2026-10-03T00:00:00Z"),
    ("EGP", "USD", 0.02061856, "2026-10-02T00:00:00Z", "2026-10-03T00:00:00Z"),
    ("USD", "JOD", 0.709, "2026-10-02T00:00:00Z", "2026-10-03T00:00:00Z"),
    ("JOD", "USD", 1.410437, "2026-10-02T00:00:00Z", "2026-10-03T00:00:00Z"),
    ("EUR", "USD", 1.17, "2026-10-02T00:00:00Z", "2026-10-03T00:00:00Z"),
    ("USD", "EUR", 0.854701, "2026-10-02T00:00:00Z", "2026-10-03T00:00:00Z"),
    ("GBP", "USD", 1.35, "2026-10-02T00:00:00Z", "2026-10-03T00:00:00Z"),
    ("USD", "GBP", 0.740741, "2026-10-02T00:00:00Z", "2026-10-03T00:00:00Z"),
]


PROFILE_UPDATES = [
    (
        "pru_001", "cus_001", "phone_number", "+201001234567",
        "+201001234568", "applied", "2026-09-15T10:00:00Z",
        "2026-09-15T10:30:00Z",
    ),
    (
        "pru_002", "cus_002", "email", "sara.ibrahim@example.com",
        "sara.new@example.com", "requested", "2026-10-01T14:20:00Z", None,
    ),
    (
        "pru_003", "cus_004", "preferred_language", "en", "ar", "applied",
        "2026-08-21T08:00:00Z", "2026-08-21T08:15:00Z",
    ),
]


ACCOUNT_CLOSURE_REQUESTS = [
    (
        "acr_001", "acc_005", "Customer is consolidating accounts",
        "under_review", "2026-10-01T09:30:00Z", None,
    ),
    (
        "acr_002", "acc_002", "Customer changed their mind", "cancelled",
        "2026-09-12T12:00:00Z", "2026-09-12T12:20:00Z",
    ),
]


CARDS = [
    (
        "card_001",
        "acc_001",
        "4242",
        "debit",
        "physical",
        "active",
        "delivered",
        12,
        2030,
        1,
    ),
    (
        "card_002",
        "acc_002",
        "8193",
        "debit",
        "physical",
        "inactive",
        "ordered",
        8,
        2031,
        0,
    ),
    (
        "card_003",
        "acc_003",
        "5501",
        "debit",
        "physical",
        "frozen",
        "delivered",
        4,
        2029,
        0,
    ),
    (
        "card_004",
        "acc_004",
        "2764",
        "debit",
        "virtual",
        "active",
        "not_applicable",
        10,
        2028,
        1,
    ),
    (
        "card_005",
        "acc_005",
        "9037",
        "debit",
        "disposable",
        "blocked",
        "not_applicable",
        6,
        2029,
        0,
    ),
]


TRANSACTIONS = [
    (
        "txn_001", "acc_001", "card_001", "card_payment", "Cairo Coffee",
        12_500, "EGP", 0, None, "completed", None,
        "2026-09-24T08:30:00Z",
    ),
    (
        "txn_002", "acc_001", "card_001", "card_payment", "Electronics Store",
        349_900, "EGP", 0, None, "declined", None,
        "2026-09-25T15:10:00Z",
    ),
    (
        "txn_003", "acc_001", "card_001", "card_payment", "City Supermarket",
        89_250, "EGP", 0, None, "pending", None,
        "2026-09-30T18:45:00Z",
    ),
    (
        "txn_004", "acc_001", "card_001", "card_payment", "Cairo Coffee",
        12_500, "EGP", 0, None, "completed", "txn_001",
        "2026-09-24T08:31:00Z",
    ),
    (
        "txn_005", "acc_001", "card_001", "cash_withdrawal", "Nile Street ATM",
        200_000, "EGP", 2_500, 150_000, "completed", None,
        "2026-09-27T20:15:00Z",
    ),
    (
        "txn_006", "acc_002", "card_002", "cash_withdrawal", "Downtown ATM",
        50_000, "EGP", 500, 50_000, "completed", None,
        "2026-09-28T11:20:00Z",
    ),
    (
        "txn_007", "acc_002", "card_002", "card_payment", "Online Books",
        15_999, "EGP", 0, None, "reversed", None,
        "2026-09-29T09:05:00Z",
    ),
    (
        "txn_008", "acc_003", None, "direct_debit", "Cloud Storage",
        2_500, "USD", 0, None, "completed", None,
        "2026-09-26T07:00:00Z",
    ),
    (
        "txn_009", "acc_004", "card_004", "card_payment", "Amman Restaurant",
        1_200, "JOD", 0, None, "completed", None,
        "2026-09-28T19:40:00Z",
    ),
    (
        "txn_010", "acc_005", None, "direct_debit", "Mobile Service",
        75_000, "EGP", 0, None, "pending", None,
        "2026-09-30T06:00:00Z",
    ),
]


REFUNDS = [
    (
        "ref_001", "txn_001", 12_500, "EGP", "processing",
        "2026-09-29T10:00:00Z", "2026-10-06", None,
    ),
    (
        "ref_002", "txn_009", 1_200, "JOD", "completed",
        "2026-09-29T09:00:00Z", "2026-10-03", "2026-09-30T14:00:00Z",
    ),
    (
        "ref_003", "txn_008", 2_500, "USD", "declined",
        "2026-09-28T12:00:00Z", None, None,
    ),
]


DISPUTES = [
    (
        "disp_001", "txn_004", "Card payment charged twice", "under_review",
        None, "2026-09-25T09:00:00Z", "2026-09-30T13:00:00Z",
    ),
    (
        "disp_002", "txn_006", "Cash withdrawal not recognized",
        "awaiting_customer", None, "2026-09-29T08:00:00Z",
        "2026-09-30T08:00:00Z",
    ),
    (
        "disp_003", "txn_005", "ATM dispensed less cash than requested",
        "resolved", "Cash discrepancy confirmed and the difference was credited",
        "2026-09-27T21:00:00Z", "2026-09-30T16:30:00Z",
    ),
]


BENEFICIARIES = [
    (
        "ben_001", "cus_001", "Mona Adel", "Nile Bank", "6789", "active",
        "2026-08-10T09:00:00Z",
    ),
    (
        "ben_002", "cus_001", "Karim Samy", "Cairo Bank", "1122", "pending",
        "2026-09-29T14:00:00Z",
    ),
    (
        "ben_003", "cus_002", "Samir Fathy", "Delta Bank", "4501", "blocked",
        "2026-07-15T12:30:00Z",
    ),
    (
        "ben_004", "cus_004", "Rana Odeh", "Amman Bank", "9087", "active",
        "2026-06-20T10:15:00Z",
    ),
    (
        "ben_005", "cus_005", "Hassan Ali", "Nile Bank", "3344", "active",
        "2026-05-05T08:45:00Z",
    ),
]


TRANSFERS = [
    (
        "trf_001", "acc_001", "ben_001", "outgoing", "Mona Adel", "Rent",
        75_000, "EGP", 500, "completed", None,
        "2026-09-20T09:00:00Z", "2026-09-20T09:02:00Z", None,
    ),
    (
        "trf_002", "acc_001", "ben_001", "outgoing", "Mona Adel", "Utilities",
        120_000, "EGP", 500, "pending", None,
        "2026-09-30T16:00:00Z", None, None,
    ),
    (
        "trf_003", "acc_001", "ben_002", "outgoing", "Karim Samy", "Shared bill",
        40_000, "EGP", 0, "declined", "Beneficiary verification is pending",
        "2026-09-30T17:00:00Z", None, None,
    ),
    (
        "trf_004", "acc_002", "ben_003", "outgoing", "Samir Fathy", None,
        25_000, "EGP", 0, "failed", "Beneficiary is blocked",
        "2026-09-28T13:00:00Z", None, None,
    ),
    (
        "trf_005", "acc_003", None, "incoming", "Acme Client", "Invoice 104",
        50_000, "USD", 0, "completed", None,
        "2026-09-27T11:00:00Z", "2026-09-27T11:01:00Z", None,
    ),
    (
        "trf_006", "acc_004", "ben_004", "outgoing", "Rana Odeh", "Dinner",
        10_000, "JOD", 0, "cancelled", None,
        "2026-09-29T20:00:00Z", None, "2026-09-29T20:03:00Z",
    ),
    (
        "trf_007", "acc_005", None, "incoming", "Youssef Trading", None,
        300_000, "EGP", 0, "pending", None,
        "2026-09-30T12:00:00Z", None, None,
    ),
]


TOPUPS = [
    (
        "top_001", "acc_001", "card", "7711", 50_000, "EGP", 0,
        "completed", None, "2026-09-25T10:00:00Z", "2026-09-25T10:01:00Z",
    ),
    (
        "top_002", "acc_001", "card", "8822", 100_000, "EGP", 1_000,
        "pending", None, "2026-09-30T19:00:00Z", None,
    ),
    (
        "top_003", "acc_002", "bank_transfer", None, 80_000, "EGP", 0,
        "failed", "Sender account could not be verified",
        "2026-09-27T08:00:00Z", None,
    ),
    (
        "top_004", "acc_003", "card", "9933", 10_000, "USD", 0,
        "reversed", "Source bank reversed the top-up",
        "2026-09-26T15:00:00Z", None,
    ),
    (
        "top_005", "acc_004", "cash", None, 20_000, "JOD", 0,
        "verification_required", "Source-of-funds verification is required",
        "2026-09-29T11:00:00Z", None,
    ),
    (
        "top_006", "acc_005", "cheque", None, 250_000, "EGP", 0,
        "pending", None, "2026-09-30T09:00:00Z", None,
    ),
]


CUSTOMER_UPSERT = """
INSERT INTO customers (
    customer_id,
    full_name,
    email,
    country,
    phone_number,
    preferred_language,
    identity_verification_status,
    updated_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(customer_id) DO UPDATE SET
    full_name = excluded.full_name,
    email = excluded.email,
    country = excluded.country,
    phone_number = excluded.phone_number,
    preferred_language = excluded.preferred_language,
    identity_verification_status = excluded.identity_verification_status,
    updated_at = excluded.updated_at
"""


ACCOUNT_UPSERT = """
INSERT INTO accounts (
    account_id,
    customer_id,
    account_number_last_four,
    account_type,
    currency,
    balance_minor_units,
    available_balance_minor_units,
    status,
    opened_at,
    closed_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(account_id) DO UPDATE SET
    customer_id = excluded.customer_id,
    account_number_last_four = excluded.account_number_last_four,
    account_type = excluded.account_type,
    currency = excluded.currency,
    balance_minor_units = excluded.balance_minor_units,
    available_balance_minor_units = excluded.available_balance_minor_units,
    status = excluded.status,
    opened_at = excluded.opened_at,
    closed_at = excluded.closed_at
"""


SUPPORTED_CURRENCY_UPSERT = """
INSERT INTO supported_currencies (
    currency_code,
    display_name,
    symbol,
    decimal_places,
    can_hold,
    can_exchange,
    enabled
)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(currency_code) DO UPDATE SET
    display_name = excluded.display_name,
    symbol = excluded.symbol,
    decimal_places = excluded.decimal_places,
    can_hold = excluded.can_hold,
    can_exchange = excluded.can_exchange,
    enabled = excluded.enabled
"""


EXCHANGE_RATE_UPSERT = """
INSERT INTO exchange_rates (
    base_currency,
    quote_currency,
    rate,
    effective_at,
    expires_at
)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(base_currency, quote_currency, effective_at) DO UPDATE SET
    rate = excluded.rate,
    expires_at = excluded.expires_at
"""


PROFILE_UPDATE_UPSERT = """
INSERT INTO customer_profile_updates (
    profile_update_id,
    customer_id,
    field_name,
    old_value,
    new_value,
    status,
    requested_at,
    completed_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(profile_update_id) DO UPDATE SET
    customer_id = excluded.customer_id,
    field_name = excluded.field_name,
    old_value = excluded.old_value,
    new_value = excluded.new_value,
    status = excluded.status,
    requested_at = excluded.requested_at,
    completed_at = excluded.completed_at
"""


ACCOUNT_CLOSURE_REQUEST_UPSERT = """
INSERT INTO account_closure_requests (
    closure_request_id,
    account_id,
    reason,
    status,
    requested_at,
    resolved_at
)
VALUES (?, ?, ?, ?, ?, ?)
ON CONFLICT(closure_request_id) DO UPDATE SET
    account_id = excluded.account_id,
    reason = excluded.reason,
    status = excluded.status,
    requested_at = excluded.requested_at,
    resolved_at = excluded.resolved_at
"""


CARD_UPSERT = """
INSERT INTO cards (
    card_id,
    account_id,
    last_four,
    card_type,
    card_form,
    status,
    delivery_status,
    expiry_month,
    expiry_year,
    contactless_enabled
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(card_id) DO UPDATE SET
    account_id = excluded.account_id,
    last_four = excluded.last_four,
    card_type = excluded.card_type,
    card_form = excluded.card_form,
    status = excluded.status,
    delivery_status = excluded.delivery_status,
    expiry_month = excluded.expiry_month,
    expiry_year = excluded.expiry_year,
    contactless_enabled = excluded.contactless_enabled
"""


TRANSACTION_UPSERT = """
INSERT INTO transactions (
    transaction_id,
    account_id,
    card_id,
    transaction_type,
    description,
    amount_minor_units,
    currency,
    fee_minor_units,
    cash_received_minor_units,
    status,
    duplicate_of_transaction_id,
    created_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(transaction_id) DO UPDATE SET
    account_id = excluded.account_id,
    card_id = excluded.card_id,
    transaction_type = excluded.transaction_type,
    description = excluded.description,
    amount_minor_units = excluded.amount_minor_units,
    currency = excluded.currency,
    fee_minor_units = excluded.fee_minor_units,
    cash_received_minor_units = excluded.cash_received_minor_units,
    status = excluded.status,
    duplicate_of_transaction_id = excluded.duplicate_of_transaction_id,
    created_at = excluded.created_at
"""


REFUND_UPSERT = """
INSERT INTO refunds (
    refund_id,
    transaction_id,
    amount_minor_units,
    currency,
    status,
    requested_at,
    expected_by,
    completed_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(refund_id) DO UPDATE SET
    transaction_id = excluded.transaction_id,
    amount_minor_units = excluded.amount_minor_units,
    currency = excluded.currency,
    status = excluded.status,
    requested_at = excluded.requested_at,
    expected_by = excluded.expected_by,
    completed_at = excluded.completed_at
"""


DISPUTE_UPSERT = """
INSERT INTO disputes (
    dispute_id,
    transaction_id,
    reason,
    status,
    resolution,
    created_at,
    updated_at
)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(dispute_id) DO UPDATE SET
    transaction_id = excluded.transaction_id,
    reason = excluded.reason,
    status = excluded.status,
    resolution = excluded.resolution,
    created_at = excluded.created_at,
    updated_at = excluded.updated_at
"""


BENEFICIARY_UPSERT = """
INSERT INTO beneficiaries (
    beneficiary_id,
    customer_id,
    name,
    bank_name,
    account_last_four,
    status,
    created_at
)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(beneficiary_id) DO UPDATE SET
    customer_id = excluded.customer_id,
    name = excluded.name,
    bank_name = excluded.bank_name,
    account_last_four = excluded.account_last_four,
    status = excluded.status,
    created_at = excluded.created_at
"""


TRANSFER_UPSERT = """
INSERT INTO transfers (
    transfer_id,
    source_account_id,
    beneficiary_id,
    direction,
    counterparty_name,
    reference,
    amount_minor_units,
    currency,
    fee_minor_units,
    status,
    failure_reason,
    created_at,
    completed_at,
    cancelled_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(transfer_id) DO UPDATE SET
    source_account_id = excluded.source_account_id,
    beneficiary_id = excluded.beneficiary_id,
    direction = excluded.direction,
    counterparty_name = excluded.counterparty_name,
    reference = excluded.reference,
    amount_minor_units = excluded.amount_minor_units,
    currency = excluded.currency,
    fee_minor_units = excluded.fee_minor_units,
    status = excluded.status,
    failure_reason = excluded.failure_reason,
    created_at = excluded.created_at,
    completed_at = excluded.completed_at,
    cancelled_at = excluded.cancelled_at
"""


TOPUP_UPSERT = """
INSERT INTO topups (
    topup_id,
    account_id,
    method,
    source_last_four,
    amount_minor_units,
    currency,
    fee_minor_units,
    status,
    failure_reason,
    created_at,
    completed_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(topup_id) DO UPDATE SET
    account_id = excluded.account_id,
    method = excluded.method,
    source_last_four = excluded.source_last_four,
    amount_minor_units = excluded.amount_minor_units,
    currency = excluded.currency,
    fee_minor_units = excluded.fee_minor_units,
    status = excluded.status,
    failure_reason = excluded.failure_reason,
    created_at = excluded.created_at,
    completed_at = excluded.completed_at
"""


def seed_database(database_path: Path = DATABASE_PATH) -> None:
    """Create the database and upsert the deterministic sample records."""
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    try:
        create_schema(connection)
        with connection:
            connection.executemany(
                SUPPORTED_CURRENCY_UPSERT,
                SUPPORTED_CURRENCIES,
            )
            connection.executemany(EXCHANGE_RATE_UPSERT, EXCHANGE_RATES)
            connection.executemany(CUSTOMER_UPSERT, CUSTOMERS)
            connection.executemany(ACCOUNT_UPSERT, ACCOUNTS)
            connection.executemany(PROFILE_UPDATE_UPSERT, PROFILE_UPDATES)
            connection.executemany(
                ACCOUNT_CLOSURE_REQUEST_UPSERT,
                ACCOUNT_CLOSURE_REQUESTS,
            )
            connection.executemany(CARD_UPSERT, CARDS)
            connection.executemany(TRANSACTION_UPSERT, TRANSACTIONS)
            connection.executemany(REFUND_UPSERT, REFUNDS)
            connection.executemany(DISPUTE_UPSERT, DISPUTES)
            connection.executemany(BENEFICIARY_UPSERT, BENEFICIARIES)
            connection.executemany(TRANSFER_UPSERT, TRANSFERS)
            connection.executemany(TOPUP_UPSERT, TOPUPS)
    finally:
        connection.close()


def main() -> None:
    seed_database()
    print(f"Synthetic bank database created at: {DATABASE_PATH}")
    print(
        f"Seeded {len(CUSTOMERS)} customers, "
        f"{len(ACCOUNTS)} accounts, {len(CARDS)} cards, "
        f"{len(TRANSACTIONS)} transactions, {len(REFUNDS)} refunds, "
        f"{len(DISPUTES)} disputes, {len(BENEFICIARIES)} beneficiaries, "
        f"{len(TRANSFERS)} transfers, {len(TOPUPS)} top-ups, "
        f"{len(SUPPORTED_CURRENCIES)} supported currencies, "
        f"{len(EXCHANGE_RATES)} exchange rates, "
        f"{len(PROFILE_UPDATES)} profile updates, and "
        f"{len(ACCOUNT_CLOSURE_REQUESTS)} account closure requests."
    )


if __name__ == "__main__":
    main()
