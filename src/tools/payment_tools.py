from langchain.tools import tool

from src.bank.database import (
    cancel_dispute,
    get_dispute_status,
    get_refund_status,
    get_transaction,
    list_recent_transactions,
    open_dispute,
    request_refund,
)


def create_payment_tools(customer_id: str):
    @tool
    def get_my_transaction(transaction_id: str) -> dict[str ,  object]:
        """Gets a transaction by searching using a transaction id"""
        transaction = get_transaction(
            customer_id=customer_id,
            transaction_id=transaction_id
        )
        if transaction is None:
            return {
                "found": False,
                "message": "No matching transaction was found."
            }
        return {
            "found": True,
            "message": transaction
        }
    @tool
    def list_my_transactions(limit: int = 10) -> list[dict[str , object]]:
        """
        Lists recent transcations , pass the limit it has a max of 50 and min of 1 and default value of 10

        """
        transactions = list_recent_transactions(
            customer_id=customer_id,
            limit=limit
        )
        return transactions
    @tool
    def get_my_refund_status(refund_id: str) -> dict[str , object]:
        """ Returns refund status when passed a valid refund id"""
        refund = get_refund_status(
            customer_id=customer_id,
            refund_id=refund_id
        )
        if refund is None:
            return {
                "found": False,
                "message": "No mathcing refund was found."
            }
        return {
            "found": True,
            "message": refund
        }
    @tool
    def get_my_dispute_status(dispute_id: str) -> dict[str , object]:
        """ Returns dispute status when passed a valid disputes id"""
        dispute = get_dispute_status(
            customer_id=customer_id,
            dispute_id=dispute_id
        )
        if dispute is None:
            return {
                "found": False,
                "message": "No mathcing dipute was found."
            }
        return {
            "found": True,
            "message": dispute
        }

    @tool
    def request_my_refund(
        transaction_id: str,
        amount_minor_units: int | None = None,
    ) -> dict[str, object]:
        """Request a refund after the customer explicitly asks for it.

        Omit amount_minor_units to request a full refund, or provide a positive
        amount in the currency's minor units for a partial refund.
        """
        try:
            refund = request_refund(
                customer_id=customer_id,
                transaction_id=transaction_id,
                amount_minor_units=amount_minor_units,
            )
        except ValueError as error:
            return {
                "success": False,
                "message": str(error),
            }

        if refund is None:
            return {
                "success": False,
                "message": "No matching transaction was found.",
            }

        return {
            "success": True,
            "refund": refund,
        }

    @tool
    def open_my_dispute(transaction_id: str, reason: str) -> dict[str, object]:
        """Open a dispute after the customer explicitly requests it."""
        try:
            dispute = open_dispute(
                customer_id=customer_id,
                transaction_id=transaction_id,
                reason=reason,
            )
        except ValueError as error:
            return {
                "success": False,
                "message": str(error),
            }

        if dispute is None:
            return {
                "success": False,
                "message": "No matching transaction was found.",
            }

        return {
            "success": True,
            "dispute": dispute,
        }

    @tool
    def cancel_my_dispute(dispute_id: str) -> dict[str, object]:
        """Cancel an unresolved dispute after an explicit customer request."""
        try:
            dispute = cancel_dispute(
                customer_id=customer_id,
                dispute_id=dispute_id,
            )
        except ValueError as error:
            return {
                "success": False,
                "message": str(error),
            }

        if dispute is None:
            return {
                "success": False,
                "message": "No matching dispute was found.",
            }

        return {
            "success": True,
            "dispute": dispute,
        }

    return [get_my_transaction,
            list_my_transactions ,
            get_my_refund_status ,
            get_my_dispute_status,
            request_my_refund,
            open_my_dispute,
            cancel_my_dispute]
