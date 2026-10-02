"""SQLite schema for the synthetic bank data."""

import sqlite3


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL,
    phone_number TEXT,
    preferred_language TEXT NOT NULL DEFAULT 'en',
    identity_verification_status TEXT NOT NULL DEFAULT 'unverified'
        CHECK (
            identity_verification_status IN (
                'unverified',
                'pending',
                'verified',
                'failed'
            )
        ),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    account_number_last_four TEXT
        CHECK (
            account_number_last_four IS NULL
            OR (
                length(account_number_last_four) = 4
                AND account_number_last_four NOT GLOB '*[^0-9]*'
            )
        ),
    account_type TEXT NOT NULL
        CHECK (account_type IN ('checking', 'savings')),
    currency TEXT NOT NULL
        CHECK (length(currency) = 3),
    balance_minor_units INTEGER NOT NULL DEFAULT 0
        CHECK (balance_minor_units >= 0),
    available_balance_minor_units INTEGER NOT NULL DEFAULT 0
        CHECK (available_balance_minor_units >= 0),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'frozen', 'closed')),
    opened_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS supported_currencies (
    currency_code TEXT PRIMARY KEY
        CHECK (length(currency_code) = 3),
    display_name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    decimal_places INTEGER NOT NULL DEFAULT 2
        CHECK (decimal_places BETWEEN 0 AND 4),
    can_hold INTEGER NOT NULL DEFAULT 1
        CHECK (can_hold IN (0, 1)),
    can_exchange INTEGER NOT NULL DEFAULT 1
        CHECK (can_exchange IN (0, 1)),
    enabled INTEGER NOT NULL DEFAULT 1
        CHECK (enabled IN (0, 1))
);

CREATE TABLE IF NOT EXISTS exchange_rates (
    base_currency TEXT NOT NULL,
    quote_currency TEXT NOT NULL,
    rate REAL NOT NULL
        CHECK (rate > 0),
    effective_at TEXT NOT NULL,
    expires_at TEXT,
    PRIMARY KEY (base_currency, quote_currency, effective_at),
    CHECK (base_currency <> quote_currency),
    FOREIGN KEY (base_currency) REFERENCES supported_currencies(currency_code)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (quote_currency) REFERENCES supported_currencies(currency_code)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS customer_profile_updates (
    profile_update_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    field_name TEXT NOT NULL
        CHECK (
            field_name IN (
                'full_name',
                'email',
                'country',
                'phone_number',
                'preferred_language'
            )
        ),
    old_value TEXT,
    new_value TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'requested'
        CHECK (status IN ('requested', 'applied', 'rejected', 'cancelled')),
    requested_at TEXT NOT NULL,
    completed_at TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS account_closure_requests (
    closure_request_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    reason TEXT,
    status TEXT NOT NULL DEFAULT 'requested'
        CHECK (
            status IN (
                'requested',
                'under_review',
                'completed',
                'rejected',
                'cancelled'
            )
        ),
    requested_at TEXT NOT NULL,
    resolved_at TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS cards (
    card_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    last_four TEXT NOT NULL
        CHECK (length(last_four) = 4 AND last_four NOT GLOB '*[^0-9]*'),
    card_type TEXT NOT NULL
        CHECK (card_type IN ('debit', 'credit')),
    card_form TEXT NOT NULL
        CHECK (card_form IN ('physical', 'virtual', 'disposable')),
    status TEXT NOT NULL DEFAULT 'inactive'
        CHECK (status IN ('inactive', 'active', 'frozen', 'blocked', 'expired')),
    delivery_status TEXT NOT NULL DEFAULT 'not_applicable'
        CHECK (
            delivery_status IN (
                'not_applicable',
                'ordered',
                'shipped',
                'delivered',
                'returned'
            )
        ),
    expiry_month INTEGER NOT NULL
        CHECK (expiry_month BETWEEN 1 AND 12),
    expiry_year INTEGER NOT NULL
        CHECK (expiry_year >= 2020),
    contactless_enabled INTEGER NOT NULL DEFAULT 0
        CHECK (contactless_enabled IN (0, 1)),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    card_id TEXT,
    transaction_type TEXT NOT NULL
        CHECK (
            transaction_type IN (
                'card_payment',
                'cash_withdrawal',
                'direct_debit'
            )
        ),
    description TEXT NOT NULL,
    amount_minor_units INTEGER NOT NULL
        CHECK (amount_minor_units > 0),
    currency TEXT NOT NULL
        CHECK (length(currency) = 3),
    fee_minor_units INTEGER NOT NULL DEFAULT 0
        CHECK (fee_minor_units >= 0),
    cash_received_minor_units INTEGER
        CHECK (
            cash_received_minor_units IS NULL
            OR cash_received_minor_units >= 0
        ),
    status TEXT NOT NULL
        CHECK (status IN ('pending', 'completed', 'declined', 'reversed')),
    duplicate_of_transaction_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (card_id) REFERENCES cards(card_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (duplicate_of_transaction_id)
        REFERENCES transactions(transaction_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS refunds (
    refund_id TEXT PRIMARY KEY,
    transaction_id TEXT NOT NULL,
    amount_minor_units INTEGER NOT NULL
        CHECK (amount_minor_units > 0),
    currency TEXT NOT NULL
        CHECK (length(currency) = 3),
    status TEXT NOT NULL
        CHECK (status IN ('requested', 'processing', 'completed', 'declined')),
    requested_at TEXT NOT NULL,
    expected_by TEXT,
    completed_at TEXT,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS disputes (
    dispute_id TEXT PRIMARY KEY,
    transaction_id TEXT NOT NULL,
    reason TEXT NOT NULL
        CHECK (length(trim(reason)) > 0),
    status TEXT NOT NULL
        CHECK (
            status IN (
                'submitted',
                'under_review',
                'awaiting_customer',
                'resolved',
                'rejected',
                'cancelled'
            )
        ),
    resolution TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS beneficiaries (
    beneficiary_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    name TEXT NOT NULL,
    bank_name TEXT NOT NULL,
    account_last_four TEXT NOT NULL
        CHECK (
            length(account_last_four) = 4
            AND account_last_four NOT GLOB '*[^0-9]*'
        ),
    status TEXT NOT NULL
        CHECK (status IN ('active', 'pending', 'blocked')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS transfers (
    transfer_id TEXT PRIMARY KEY,
    source_account_id TEXT NOT NULL,
    beneficiary_id TEXT,
    direction TEXT NOT NULL
        CHECK (direction IN ('incoming', 'outgoing')),
    counterparty_name TEXT NOT NULL,
    reference TEXT,
    amount_minor_units INTEGER NOT NULL
        CHECK (amount_minor_units > 0),
    currency TEXT NOT NULL
        CHECK (length(currency) = 3),
    fee_minor_units INTEGER NOT NULL DEFAULT 0
        CHECK (fee_minor_units >= 0),
    status TEXT NOT NULL
        CHECK (
            status IN (
                'pending',
                'completed',
                'failed',
                'declined',
                'cancelled'
            )
        ),
    failure_reason TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    cancelled_at TEXT,
    CHECK (direction = 'incoming' OR beneficiary_id IS NOT NULL),
    FOREIGN KEY (source_account_id) REFERENCES accounts(account_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS topups (
    topup_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    method TEXT NOT NULL
        CHECK (method IN ('card', 'bank_transfer', 'cash', 'cheque')),
    source_last_four TEXT
        CHECK (
            source_last_four IS NULL
            OR (
                length(source_last_four) = 4
                AND source_last_four NOT GLOB '*[^0-9]*'
            )
        ),
    amount_minor_units INTEGER NOT NULL
        CHECK (amount_minor_units > 0),
    currency TEXT NOT NULL
        CHECK (length(currency) = 3),
    fee_minor_units INTEGER NOT NULL DEFAULT 0
        CHECK (fee_minor_units >= 0),
    status TEXT NOT NULL
        CHECK (
            status IN (
                'pending',
                'completed',
                'failed',
                'reversed',
                'verification_required'
            )
        ),
    failure_reason TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_accounts_customer_id
    ON accounts(customer_id);

CREATE INDEX IF NOT EXISTS idx_exchange_rates_pair_effective_at
    ON exchange_rates(base_currency, quote_currency, effective_at DESC);

CREATE INDEX IF NOT EXISTS idx_profile_updates_customer_requested_at
    ON customer_profile_updates(customer_id, requested_at DESC);

CREATE INDEX IF NOT EXISTS idx_closure_requests_account_requested_at
    ON account_closure_requests(account_id, requested_at DESC);

CREATE INDEX IF NOT EXISTS idx_cards_account_id
    ON cards(account_id);

CREATE INDEX IF NOT EXISTS idx_transactions_account_created_at
    ON transactions(account_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_card_id
    ON transactions(card_id);

CREATE INDEX IF NOT EXISTS idx_refunds_transaction_id
    ON refunds(transaction_id);

CREATE INDEX IF NOT EXISTS idx_disputes_transaction_id
    ON disputes(transaction_id);

CREATE INDEX IF NOT EXISTS idx_beneficiaries_customer_id
    ON beneficiaries(customer_id);

CREATE INDEX IF NOT EXISTS idx_transfers_account_created_at
    ON transfers(source_account_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_transfers_beneficiary_id
    ON transfers(beneficiary_id);

CREATE INDEX IF NOT EXISTS idx_topups_account_created_at
    ON topups(account_id, created_at DESC);
"""


CUSTOMER_COLUMN_MIGRATIONS = {
    "phone_number": "phone_number TEXT",
    "preferred_language": "preferred_language TEXT NOT NULL DEFAULT 'en'",
    "identity_verification_status": (
        "identity_verification_status TEXT NOT NULL DEFAULT 'unverified' "
        "CHECK (identity_verification_status IN "
        "('unverified', 'pending', 'verified', 'failed'))"
    ),
    "updated_at": "updated_at TEXT",
}


ACCOUNT_COLUMN_MIGRATIONS = {
    "account_number_last_four": (
        "account_number_last_four TEXT CHECK ("
        "account_number_last_four IS NULL OR ("
        "length(account_number_last_four) = 4 AND "
        "account_number_last_four NOT GLOB '*[^0-9]*'))"
    ),
    "available_balance_minor_units": (
        "available_balance_minor_units INTEGER NOT NULL DEFAULT 0 "
        "CHECK (available_balance_minor_units >= 0)"
    ),
    "opened_at": "opened_at TEXT",
    "closed_at": "closed_at TEXT",
}


def _add_missing_columns(
    connection: sqlite3.Connection,
    table_name: str,
    columns: dict[str, str],
) -> set[str]:
    """Add columns introduced after the first synthetic database version."""
    existing_columns = {
        row[1]
        for row in connection.execute(f"PRAGMA table_info({table_name})")
    }
    added_columns = set()

    for column_name, column_definition in columns.items():
        if column_name in existing_columns:
            continue

        connection.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_definition}"
        )
        added_columns.add(column_name)

    return added_columns


def create_schema(connection: sqlite3.Connection) -> None:
    """Create the synthetic-bank tables and enable foreign-key enforcement."""
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA_SQL)

    _add_missing_columns(connection, "customers", CUSTOMER_COLUMN_MIGRATIONS)
    added_account_columns = _add_missing_columns(
        connection,
        "accounts",
        ACCOUNT_COLUMN_MIGRATIONS,
    )

    # Existing accounts had only one balance value, so preserve that value as
    # both the current and available balance during the migration.
    if "available_balance_minor_units" in added_account_columns:
        connection.execute(
            """
            UPDATE accounts
            SET available_balance_minor_units = balance_minor_units
            """
        )
