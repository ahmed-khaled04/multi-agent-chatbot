"""Access helpers for the synthetic bank database."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "synthetic" / "bank.db"


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


def _new_identifier(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
