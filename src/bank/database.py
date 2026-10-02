"""Access helpers for the synthetic bank database."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "synthetic" / "bank.db"


ACCOUNT_SELECT = """
SELECT
    accounts.account_id,
    accounts.account_number_last_four,
    accounts.account_type,
    accounts.currency,
    accounts.balance_minor_units,
    accounts.available_balance_minor_units,
    accounts.status,
    accounts.opened_at,
    accounts.closed_at
FROM accounts
"""


CARD_SELECT = """
SELECT
    cards.card_id,
    cards.account_id,
    cards.last_four,
    cards.card_type,
    cards.card_form,
    cards.status,
    cards.delivery_status,
    cards.expiry_month,
    cards.expiry_year,
    cards.contactless_enabled,
    accounts.currency,
    accounts.status AS account_status
FROM cards
JOIN accounts ON accounts.account_id = cards.account_id
"""


TRANSACTION_SELECT = """
SELECT
    transactions.transaction_id,
    transactions.account_id,
    transactions.card_id,
    transactions.transaction_type,
    transactions.description,
    transactions.amount_minor_units,
    transactions.currency,
    transactions.fee_minor_units,
    transactions.cash_received_minor_units,
    transactions.status,
    transactions.duplicate_of_transaction_id,
    transactions.created_at,
    cards.last_four
FROM transactions
JOIN accounts ON accounts.account_id = transactions.account_id
LEFT JOIN cards ON cards.card_id = transactions.card_id
"""


BENEFICIARY_SELECT = """
SELECT
    beneficiaries.beneficiary_id,
    beneficiaries.name,
    beneficiaries.bank_name,
    beneficiaries.account_last_four,
    beneficiaries.status,
    beneficiaries.created_at
FROM beneficiaries
"""


TRANSFER_SELECT = """
SELECT
    transfers.transfer_id,
    transfers.source_account_id,
    transfers.beneficiary_id,
    transfers.direction,
    transfers.counterparty_name,
    transfers.reference,
    transfers.amount_minor_units,
    transfers.currency,
    transfers.fee_minor_units,
    transfers.status,
    transfers.failure_reason,
    transfers.created_at,
    transfers.completed_at,
    transfers.cancelled_at,
    beneficiaries.bank_name AS beneficiary_bank_name,
    beneficiaries.account_last_four AS beneficiary_account_last_four,
    beneficiaries.status AS beneficiary_status
FROM transfers
JOIN accounts ON accounts.account_id = transfers.source_account_id
LEFT JOIN beneficiaries
    ON beneficiaries.beneficiary_id = transfers.beneficiary_id
"""


TOPUP_SELECT = """
SELECT
    topups.topup_id,
    topups.account_id,
    topups.method,
    topups.source_last_four,
    topups.amount_minor_units,
    topups.currency,
    topups.fee_minor_units,
    topups.status,
    topups.failure_reason,
    topups.created_at,
    topups.completed_at
FROM topups
JOIN accounts ON accounts.account_id = topups.account_id
"""


def connect_database(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
    read_only: bool = True,
) -> sqlite3.Connection:
    """Open the synthetic database, using read-only mode by default."""
    path = Path(database_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(
            f"Synthetic bank database was not found: {path}. "
            "Run `python -m scripts.create_synthetic_bank` first."
        )

    if read_only:
        connection = sqlite3.connect(
            f"{path.as_uri()}?mode=ro",
            uri=True,
        )
    else:
        connection = sqlite3.connect(path)

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    if read_only:
        connection.execute("PRAGMA query_only = ON")
    return connection


def list_customer_accounts(
    customer_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> list[dict[str, object]]:
    """Return every account belonging to the specified customer."""
    _validate_identifier(customer_id, "customer_id")

    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            ACCOUNT_SELECT
            + """
            WHERE accounts.customer_id = ?
            ORDER BY accounts.opened_at, accounts.account_id
            """,
            (customer_id,),
        ).fetchall()
    finally:
        connection.close()

    return [_account_row_to_dict(row) for row in rows]


def get_account_details(
    customer_id: str,
    account_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Return an account only when it belongs to the specified customer."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(account_id, "account_id")

    connection = connect_database(database_path)
    try:
        row = connection.execute(
            ACCOUNT_SELECT
            + """
            WHERE accounts.customer_id = ? AND accounts.account_id = ?
            """,
            (customer_id, account_id),
        ).fetchone()
    finally:
        connection.close()

    return _account_row_to_dict(row) if row is not None else None


def get_account_balance(
    customer_id: str,
    account_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Return current and available balances for a customer-owned account."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(account_id, "account_id")

    connection = connect_database(database_path)
    try:
        row = connection.execute(
            """
            SELECT
                accounts.account_id,
                accounts.account_number_last_four,
                accounts.currency,
                accounts.balance_minor_units,
                accounts.available_balance_minor_units,
                accounts.status
            FROM accounts
            WHERE accounts.customer_id = ? AND accounts.account_id = ?
            """,
            (customer_id, account_id),
        ).fetchone()
    finally:
        connection.close()

    return _account_row_to_dict(row) if row is not None else None


def list_supported_currencies(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> list[dict[str, object]]:
    """Return enabled currencies and their supported bank operations."""
    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            """
            SELECT
                currency_code,
                display_name,
                symbol,
                decimal_places,
                can_hold,
                can_exchange
            FROM supported_currencies
            WHERE enabled = 1
            ORDER BY currency_code
            """
        ).fetchall()
    finally:
        connection.close()

    currencies = []
    for row in rows:
        currency = dict(row)
        currency["can_hold"] = bool(currency["can_hold"])
        currency["can_exchange"] = bool(currency["can_exchange"])
        currencies.append(currency)
    return currencies


def get_exchange_rate(
    base_currency: str,
    quote_currency: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Return the latest currently effective synthetic exchange rate."""
    base_code = _normalize_currency_code(base_currency, "base_currency")
    quote_code = _normalize_currency_code(quote_currency, "quote_currency")
    if base_code == quote_code:
        raise ValueError("base_currency and quote_currency must be different")

    now = _utc_now()
    connection = connect_database(database_path)
    try:
        row = connection.execute(
            """
            SELECT
                exchange_rates.base_currency,
                exchange_rates.quote_currency,
                exchange_rates.rate,
                exchange_rates.effective_at,
                exchange_rates.expires_at
            FROM exchange_rates
            JOIN supported_currencies AS base
                ON base.currency_code = exchange_rates.base_currency
            JOIN supported_currencies AS quote
                ON quote.currency_code = exchange_rates.quote_currency
            WHERE exchange_rates.base_currency = ?
              AND exchange_rates.quote_currency = ?
              AND exchange_rates.effective_at <= ?
              AND (
                  exchange_rates.expires_at IS NULL
                  OR exchange_rates.expires_at > ?
              )
              AND base.enabled = 1
              AND quote.enabled = 1
              AND base.can_exchange = 1
              AND quote.can_exchange = 1
            ORDER BY exchange_rates.effective_at DESC
            LIMIT 1
            """,
            (base_code, quote_code, now, now),
        ).fetchone()
    finally:
        connection.close()

    return dict(row) if row is not None else None


def request_profile_update(
    customer_id: str,
    field_name: str,
    new_value: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Create a reviewable request to change an allowed customer field."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(field_name, "field_name")
    _validate_identifier(new_value, "new_value")

    allowed_fields = {
        "full_name",
        "email",
        "country",
        "phone_number",
        "preferred_language",
    }
    normalized_field = field_name.strip().lower()
    if normalized_field not in allowed_fields:
        raise ValueError(
            "field_name must be one of: " + ", ".join(sorted(allowed_fields))
        )

    cleaned_value = new_value.strip()
    connection = connect_database(database_path, read_only=False)
    try:
        with connection:
            customer = connection.execute(
                f"SELECT {normalized_field} FROM customers WHERE customer_id = ?",
                (customer_id,),
            ).fetchone()
            if customer is None:
                return None

            old_value = customer[normalized_field]
            if old_value == cleaned_value:
                raise ValueError(f"{normalized_field} already has this value")

            if normalized_field == "email":
                email_owner = connection.execute(
                    """
                    SELECT customer_id
                    FROM customers
                    WHERE lower(email) = lower(?) AND customer_id != ?
                    """,
                    (cleaned_value, customer_id),
                ).fetchone()
                if email_owner is not None:
                    raise ValueError("That email address is already in use")

            active_request = connection.execute(
                """
                SELECT profile_update_id
                FROM customer_profile_updates
                WHERE customer_id = ?
                  AND field_name = ?
                  AND status = 'requested'
                LIMIT 1
                """,
                (customer_id, normalized_field),
            ).fetchone()
            if active_request is not None:
                raise ValueError(
                    f"A {normalized_field} update request is already pending"
                )

            profile_update_id = _new_identifier("pru")
            requested_at = _utc_now()
            connection.execute(
                """
                INSERT INTO customer_profile_updates (
                    profile_update_id,
                    customer_id,
                    field_name,
                    old_value,
                    new_value,
                    status,
                    requested_at,
                    completed_at
                ) VALUES (?, ?, ?, ?, ?, 'requested', ?, NULL)
                """,
                (
                    profile_update_id,
                    customer_id,
                    normalized_field,
                    old_value,
                    cleaned_value,
                    requested_at,
                ),
            )

            return {
                "profile_update_id": profile_update_id,
                "field_name": normalized_field,
                "old_value": old_value,
                "new_value": cleaned_value,
                "status": "requested",
                "requested_at": requested_at,
            }
    finally:
        connection.close()


def request_account_closure(
    customer_id: str,
    account_id: str,
    reason: str | None = None,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Create a closure request for a customer-owned account."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(account_id, "account_id")
    if reason is not None:
        _validate_identifier(reason, "reason")

    cleaned_reason = reason.strip() if reason is not None else None
    connection = connect_database(database_path, read_only=False)
    try:
        with connection:
            account = connection.execute(
                """
                SELECT account_id, status
                FROM accounts
                WHERE customer_id = ? AND account_id = ?
                """,
                (customer_id, account_id),
            ).fetchone()
            if account is None:
                return None
            if account["status"] == "closed":
                raise ValueError("The account is already closed")

            active_request = connection.execute(
                """
                SELECT closure_request_id, status, requested_at
                FROM account_closure_requests
                WHERE account_id = ?
                  AND status IN ('requested', 'under_review')
                ORDER BY requested_at DESC
                LIMIT 1
                """,
                (account_id,),
            ).fetchone()
            if active_request is not None:
                return {
                    "closure_request_id": active_request["closure_request_id"],
                    "account_id": account_id,
                    "status": active_request["status"],
                    "requested_at": active_request["requested_at"],
                    "changed": False,
                }

            closure_request_id = _new_identifier("acr")
            requested_at = _utc_now()
            connection.execute(
                """
                INSERT INTO account_closure_requests (
                    closure_request_id,
                    account_id,
                    reason,
                    status,
                    requested_at,
                    resolved_at
                ) VALUES (?, ?, ?, 'requested', ?, NULL)
                """,
                (
                    closure_request_id,
                    account_id,
                    cleaned_reason,
                    requested_at,
                ),
            )

            return {
                "closure_request_id": closure_request_id,
                "account_id": account_id,
                "reason": cleaned_reason,
                "status": "requested",
                "requested_at": requested_at,
                "changed": True,
            }
    finally:
        connection.close()


def get_card_status(
    customer_id: str,
    card_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Return a card only when it belongs to the specified customer."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(card_id, "card_id")

    connection = connect_database(database_path)
    try:
        row = connection.execute(
            CARD_SELECT
            + """
            WHERE accounts.customer_id = ? AND cards.card_id = ?
            """,
            (customer_id, card_id),
        ).fetchone()
    finally:
        connection.close()

    return _card_row_to_dict(row) if row is not None else None


def list_customer_cards(
    customer_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> list[dict[str, object]]:
    """Return all cards belonging to the specified customer."""
    _validate_identifier(customer_id, "customer_id")

    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            CARD_SELECT
            + """
            WHERE accounts.customer_id = ?
            ORDER BY cards.card_id
            """,
            (customer_id,),
        ).fetchall()
    finally:
        connection.close()

    return [_card_row_to_dict(row) for row in rows]


def list_recent_transactions(
    customer_id: str,
    limit: int = 10,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> list[dict[str, object]]:
    """Return the customer's most recent transactions."""
    _validate_identifier(customer_id, "customer_id")
    _validate_limit(limit)

    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            TRANSACTION_SELECT
            + """
            WHERE accounts.customer_id = ?
            ORDER BY transactions.created_at DESC, transactions.transaction_id
            LIMIT ?
            """,
            (customer_id, limit),
        ).fetchall()
    finally:
        connection.close()

    return [_transaction_row_to_dict(row) for row in rows]


def get_transaction(
    customer_id: str,
    transaction_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Return a transaction only when it belongs to the specified customer."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(transaction_id, "transaction_id")

    connection = connect_database(database_path)
    try:
        row = connection.execute(
            TRANSACTION_SELECT
            + """
            WHERE accounts.customer_id = ?
              AND transactions.transaction_id = ?
            """,
            (customer_id, transaction_id),
        ).fetchone()
    finally:
        connection.close()

    return _transaction_row_to_dict(row) if row is not None else None


def get_refund_status(
    customer_id: str,
    refund_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Return a refund only when its transaction belongs to the customer."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(refund_id, "refund_id")

    connection = connect_database(database_path)
    try:
        row = connection.execute(
            """
            SELECT
                refunds.refund_id,
                refunds.transaction_id,
                refunds.amount_minor_units,
                refunds.currency,
                refunds.status,
                refunds.requested_at,
                refunds.expected_by,
                refunds.completed_at,
                transactions.description AS transaction_description,
                transactions.status AS transaction_status
            FROM refunds
            JOIN transactions
                ON transactions.transaction_id = refunds.transaction_id
            JOIN accounts ON accounts.account_id = transactions.account_id
            WHERE accounts.customer_id = ? AND refunds.refund_id = ?
            """,
            (customer_id, refund_id),
        ).fetchone()
    finally:
        connection.close()

    return dict(row) if row is not None else None


def get_dispute_status(
    customer_id: str,
    dispute_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Return a dispute only when its transaction belongs to the customer."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(dispute_id, "dispute_id")

    connection = connect_database(database_path)
    try:
        row = connection.execute(
            """
            SELECT
                disputes.dispute_id,
                disputes.transaction_id,
                disputes.reason,
                disputes.status,
                disputes.resolution,
                disputes.created_at,
                disputes.updated_at,
                transactions.description AS transaction_description,
                transactions.amount_minor_units AS transaction_amount_minor_units,
                transactions.currency AS transaction_currency,
                transactions.status AS transaction_status
            FROM disputes
            JOIN transactions
                ON transactions.transaction_id = disputes.transaction_id
            JOIN accounts ON accounts.account_id = transactions.account_id
            WHERE accounts.customer_id = ? AND disputes.dispute_id = ?
            """,
            (customer_id, dispute_id),
        ).fetchone()
    finally:
        connection.close()

    return dict(row) if row is not None else None


def list_customer_beneficiaries(
    customer_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> list[dict[str, object]]:
    """Return all beneficiaries belonging to the customer."""
    _validate_identifier(customer_id, "customer_id")

    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            BENEFICIARY_SELECT
            + """
            WHERE beneficiaries.customer_id = ?
            ORDER BY beneficiaries.name, beneficiaries.beneficiary_id
            """,
            (customer_id,),
        ).fetchall()
    finally:
        connection.close()

    return [_beneficiary_row_to_dict(row) for row in rows]


def list_recent_transfers(
    customer_id: str,
    limit: int = 10,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> list[dict[str, object]]:
    """Return the customer's most recent incoming and outgoing transfers."""
    _validate_identifier(customer_id, "customer_id")
    _validate_limit(limit)

    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            TRANSFER_SELECT
            + """
            WHERE accounts.customer_id = ?
            ORDER BY transfers.created_at DESC, transfers.transfer_id
            LIMIT ?
            """,
            (customer_id, limit),
        ).fetchall()
    finally:
        connection.close()

    return [_transfer_row_to_dict(row) for row in rows]


def get_transfer_status(
    customer_id: str,
    transfer_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Return a transfer only when it belongs to the customer."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(transfer_id, "transfer_id")

    connection = connect_database(database_path)
    try:
        row = connection.execute(
            TRANSFER_SELECT
            + """
            WHERE accounts.customer_id = ? AND transfers.transfer_id = ?
            """,
            (customer_id, transfer_id),
        ).fetchone()
    finally:
        connection.close()

    return _transfer_row_to_dict(row) if row is not None else None


def cancel_transfer(
    customer_id: str,
    transfer_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Cancel a pending transfer belonging to the customer."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(transfer_id, "transfer_id")

    connection = connect_database(database_path, read_only=False)
    try:
        with connection:
            transfer = connection.execute(
                """
                SELECT transfers.transfer_id, transfers.status
                FROM transfers
                JOIN accounts ON accounts.account_id = transfers.source_account_id
                WHERE accounts.customer_id = ? AND transfers.transfer_id = ?
                """,
                (customer_id, transfer_id),
            ).fetchone()

            if transfer is None:
                return None

            previous_status = transfer["status"]
            if previous_status == "cancelled":
                return {
                    "transfer_id": transfer_id,
                    "previous_status": previous_status,
                    "status": "cancelled",
                    "changed": False,
                }
            if previous_status != "pending":
                raise ValueError(f"A {previous_status} transfer cannot be cancelled")

            cancelled_at = _utc_now()
            connection.execute(
                """
                UPDATE transfers
                SET status = 'cancelled', cancelled_at = ?
                WHERE transfer_id = ?
                  AND source_account_id IN (
                      SELECT account_id
                      FROM accounts
                      WHERE customer_id = ?
                  )
                """,
                (cancelled_at, transfer_id, customer_id),
            )

            return {
                "transfer_id": transfer_id,
                "previous_status": previous_status,
                "status": "cancelled",
                "changed": True,
                "cancelled_at": cancelled_at,
            }
    finally:
        connection.close()


def list_recent_topups(
    customer_id: str,
    limit: int = 10,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> list[dict[str, object]]:
    """Return the customer's most recent top-ups."""
    _validate_identifier(customer_id, "customer_id")
    _validate_limit(limit)

    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            TOPUP_SELECT
            + """
            WHERE accounts.customer_id = ?
            ORDER BY topups.created_at DESC, topups.topup_id
            LIMIT ?
            """,
            (customer_id, limit),
        ).fetchall()
    finally:
        connection.close()

    return [_topup_row_to_dict(row) for row in rows]


def get_topup_status(
    customer_id: str,
    topup_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Return a top-up only when it belongs to the customer."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(topup_id, "topup_id")

    connection = connect_database(database_path)
    try:
        row = connection.execute(
            TOPUP_SELECT
            + """
            WHERE accounts.customer_id = ? AND topups.topup_id = ?
            """,
            (customer_id, topup_id),
        ).fetchone()
    finally:
        connection.close()

    return _topup_row_to_dict(row) if row is not None else None


def request_refund(
    customer_id: str,
    transaction_id: str,
    amount_minor_units: int | None = None,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Request a full or partial refund for a completed customer transaction."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(transaction_id, "transaction_id")
    if amount_minor_units is not None:
        _validate_positive_amount(amount_minor_units)

    connection = connect_database(database_path, read_only=False)
    try:
        with connection:
            transaction = connection.execute(
                """
                SELECT
                    transactions.transaction_id,
                    transactions.amount_minor_units,
                    transactions.currency,
                    transactions.status
                FROM transactions
                JOIN accounts ON accounts.account_id = transactions.account_id
                WHERE accounts.customer_id = ?
                  AND transactions.transaction_id = ?
                """,
                (customer_id, transaction_id),
            ).fetchone()

            if transaction is None:
                return None
            if transaction["status"] != "completed":
                raise ValueError("Only completed transactions can be refunded")

            refund_amount = (
                transaction["amount_minor_units"]
                if amount_minor_units is None
                else amount_minor_units
            )
            already_requested = connection.execute(
                """
                SELECT COALESCE(SUM(amount_minor_units), 0)
                FROM refunds
                WHERE transaction_id = ? AND status != 'declined'
                """,
                (transaction_id,),
            ).fetchone()[0]

            if already_requested + refund_amount > transaction["amount_minor_units"]:
                raise ValueError("Refund amount exceeds the remaining refundable amount")

            refund_id = _new_identifier("ref")
            requested_at = _utc_now()
            connection.execute(
                """
                INSERT INTO refunds (
                    refund_id,
                    transaction_id,
                    amount_minor_units,
                    currency,
                    status,
                    requested_at,
                    expected_by,
                    completed_at
                ) VALUES (?, ?, ?, ?, 'requested', ?, NULL, NULL)
                """,
                (
                    refund_id,
                    transaction_id,
                    refund_amount,
                    transaction["currency"],
                    requested_at,
                ),
            )

            return {
                "refund_id": refund_id,
                "transaction_id": transaction_id,
                "amount_minor_units": refund_amount,
                "currency": transaction["currency"],
                "status": "requested",
                "requested_at": requested_at,
            }
    finally:
        connection.close()


def open_dispute(
    customer_id: str,
    transaction_id: str,
    reason: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Open a dispute for a transaction belonging to the customer."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(transaction_id, "transaction_id")
    _validate_identifier(reason, "reason")

    connection = connect_database(database_path, read_only=False)
    try:
        with connection:
            transaction = connection.execute(
                """
                SELECT transactions.transaction_id
                FROM transactions
                JOIN accounts ON accounts.account_id = transactions.account_id
                WHERE accounts.customer_id = ?
                  AND transactions.transaction_id = ?
                """,
                (customer_id, transaction_id),
            ).fetchone()

            if transaction is None:
                return None

            active_dispute = connection.execute(
                """
                SELECT dispute_id
                FROM disputes
                WHERE transaction_id = ?
                  AND status IN ('submitted', 'under_review', 'awaiting_customer')
                """,
                (transaction_id,),
            ).fetchone()
            if active_dispute is not None:
                raise ValueError("An active dispute already exists for this transaction")

            dispute_id = _new_identifier("disp")
            created_at = _utc_now()
            connection.execute(
                """
                INSERT INTO disputes (
                    dispute_id,
                    transaction_id,
                    reason,
                    status,
                    resolution,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, 'submitted', NULL, ?, ?)
                """,
                (dispute_id, transaction_id, reason.strip(), created_at, created_at),
            )

            return {
                "dispute_id": dispute_id,
                "transaction_id": transaction_id,
                "reason": reason.strip(),
                "status": "submitted",
                "created_at": created_at,
            }
    finally:
        connection.close()


def cancel_dispute(
    customer_id: str,
    dispute_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Cancel an unresolved dispute belonging to the customer."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(dispute_id, "dispute_id")

    connection = connect_database(database_path, read_only=False)
    try:
        with connection:
            dispute = connection.execute(
                """
                SELECT disputes.dispute_id, disputes.transaction_id, disputes.status
                FROM disputes
                JOIN transactions
                    ON transactions.transaction_id = disputes.transaction_id
                JOIN accounts ON accounts.account_id = transactions.account_id
                WHERE accounts.customer_id = ? AND disputes.dispute_id = ?
                """,
                (customer_id, dispute_id),
            ).fetchone()

            if dispute is None:
                return None

            previous_status = dispute["status"]
            if previous_status == "cancelled":
                return {
                    "dispute_id": dispute_id,
                    "transaction_id": dispute["transaction_id"],
                    "previous_status": previous_status,
                    "status": "cancelled",
                    "changed": False,
                }
            if previous_status in {"resolved", "rejected"}:
                raise ValueError(f"A {previous_status} dispute cannot be cancelled")

            updated_at = _utc_now()
            connection.execute(
                """
                UPDATE disputes
                SET
                    status = 'cancelled',
                    resolution = 'Cancelled by customer',
                    updated_at = ?
                WHERE dispute_id = ?
                  AND transaction_id IN (
                      SELECT transactions.transaction_id
                      FROM transactions
                      JOIN accounts
                          ON accounts.account_id = transactions.account_id
                      WHERE accounts.customer_id = ?
                  )
                """,
                (updated_at, dispute_id, customer_id),
            )

            return {
                "dispute_id": dispute_id,
                "transaction_id": dispute["transaction_id"],
                "previous_status": previous_status,
                "status": "cancelled",
                "changed": True,
                "updated_at": updated_at,
            }
    finally:
        connection.close()


def block_card(
    customer_id: str,
    card_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, object] | None:
    """Block a card belonging to the specified customer."""
    _validate_identifier(customer_id, "customer_id")
    _validate_identifier(card_id, "card_id")

    connection = connect_database(database_path, read_only=False)
    try:
        with connection:
            row = connection.execute(
                """
                SELECT cards.card_id, cards.last_four, cards.status
                FROM cards
                JOIN accounts ON accounts.account_id = cards.account_id
                WHERE accounts.customer_id = ? AND cards.card_id = ?
                """,
                (customer_id, card_id),
            ).fetchone()

            if row is None:
                return None

            previous_status = row["status"]
            changed = previous_status != "blocked"

            if changed:
                connection.execute(
                    """
                    UPDATE cards
                    SET status = 'blocked'
                    WHERE card_id = ?
                      AND account_id IN (
                          SELECT account_id
                          FROM accounts
                          WHERE customer_id = ?
                      )
                    """,
                    (card_id, customer_id),
                )

            return {
                "card_id": row["card_id"],
                "masked_card_number": f"**** {row['last_four']}",
                "previous_status": previous_status,
                "status": "blocked",
                "changed": changed,
            }
    finally:
        connection.close()


def _account_row_to_dict(row: sqlite3.Row) -> dict[str, object]:
    account = dict(row)
    last_four = account.pop("account_number_last_four")
    account["masked_account_number"] = (
        f"**** {last_four}" if last_four is not None else None
    )
    return account


def _card_row_to_dict(row: sqlite3.Row) -> dict[str, object]:
    card = dict(row)
    card["contactless_enabled"] = bool(card["contactless_enabled"])
    card["masked_card_number"] = f"**** {card['last_four']}"
    return card


def _transaction_row_to_dict(row: sqlite3.Row) -> dict[str, object]:
    transaction = dict(row)
    last_four = transaction.pop("last_four")
    transaction["masked_card_number"] = (
        f"**** {last_four}" if last_four is not None else None
    )
    return transaction


def _beneficiary_row_to_dict(row: sqlite3.Row) -> dict[str, object]:
    beneficiary = dict(row)
    last_four = beneficiary.pop("account_last_four")
    beneficiary["masked_account_reference"] = f"**** {last_four}"
    return beneficiary


def _transfer_row_to_dict(row: sqlite3.Row) -> dict[str, object]:
    transfer = dict(row)
    last_four = transfer.pop("beneficiary_account_last_four")
    transfer["masked_beneficiary_account"] = (
        f"**** {last_four}" if last_four is not None else None
    )
    return transfer


def _topup_row_to_dict(row: sqlite3.Row) -> dict[str, object]:
    topup = dict(row)
    last_four = topup.pop("source_last_four")
    topup["masked_source_card"] = (
        f"**** {last_four}" if last_four is not None else None
    )
    return topup


def _validate_identifier(value: str, field_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    if not value.strip():
        raise ValueError(f"{field_name} cannot be empty")


def _validate_limit(limit: int) -> None:
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("limit must be an integer")
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")


def _validate_positive_amount(amount: int) -> None:
    if not isinstance(amount, int) or isinstance(amount, bool):
        raise TypeError("amount_minor_units must be an integer")
    if amount <= 0:
        raise ValueError("amount_minor_units must be greater than zero")


def _normalize_currency_code(value: str, field_name: str) -> str:
    _validate_identifier(value, field_name)
    currency_code = value.strip().upper()
    if len(currency_code) != 3 or not currency_code.isalpha():
        raise ValueError(f"{field_name} must be a three-letter currency code")
    return currency_code


def _new_identifier(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
