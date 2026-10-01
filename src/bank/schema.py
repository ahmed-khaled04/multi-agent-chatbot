"""SQLite schema for the synthetic bank data."""

import sqlite3


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    account_type TEXT NOT NULL
        CHECK (account_type IN ('checking', 'savings')),
    currency TEXT NOT NULL
        CHECK (length(currency) = 3),
    balance_minor_units INTEGER NOT NULL DEFAULT 0
        CHECK (balance_minor_units >= 0),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'frozen', 'closed')),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
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


def create_schema(connection: sqlite3.Connection) -> None:
    """Create the synthetic-bank tables and enable foreign-key enforcement."""
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA_SQL)
