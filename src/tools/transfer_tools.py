from langchain.tools import tool

from src.bank.database import (
    cancel_transfer,
    get_topup_status,
    get_transfer_status,
    list_customer_beneficiaries,
    list_recent_topups,
    list_recent_transfers,
)


def create_transfer_tools(customer_id: str):
    @tool
    def list_my_beneficiaries() -> list[dict[str, object]]:
        """List the customer's transfer beneficiaries with masked details."""
        return list_customer_beneficiaries(customer_id=customer_id)

    @tool
    def list_my_transfers(limit: int = 10) -> list[dict[str, object]]:
        """List the customer's recent incoming and outgoing transfers.

        The limit must be between 1 and 50 and defaults to 10.
        """
        return list_recent_transfers(
            customer_id=customer_id,
            limit=limit,
        )

    @tool
    def get_my_transfer_status(transfer_id: str) -> dict[str, object]:
        """Get the status and details of one customer transfer by its ID."""
        transfer = get_transfer_status(
            customer_id=customer_id,
            transfer_id=transfer_id,
        )

        if transfer is None:
            return {
                "found": False,
                "message": "No matching transfer was found.",
            }

        return {
            "found": True,
            "transfer": transfer,
        }

    @tool
    def cancel_my_transfer(transfer_id: str) -> dict[str, object]:
        """Cancel a pending transfer after an explicit customer request."""
        try:
            transfer = cancel_transfer(
                customer_id=customer_id,
                transfer_id=transfer_id,
            )
        except ValueError as error:
            return {
                "success": False,
                "message": str(error),
            }

        if transfer is None:
            return {
                "success": False,
                "message": "No matching transfer was found.",
            }

        return {
            "success": True,
            "transfer": transfer,
        }

    @tool
    def list_my_topups(limit: int = 10) -> list[dict[str, object]]:
        """List the customer's recent account top-ups.

        The limit must be between 1 and 50 and defaults to 10.
        """
        return list_recent_topups(
            customer_id=customer_id,
            limit=limit,
        )

    @tool
    def get_my_topup_status(topup_id: str) -> dict[str, object]:
        """Get the status and details of one customer top-up by its ID."""
        topup = get_topup_status(
            customer_id=customer_id,
            topup_id=topup_id,
        )

        if topup is None:
            return {
                "found": False,
                "message": "No matching top-up was found.",
            }

        return {
            "found": True,
            "topup": topup,
        }

    return [
        list_my_beneficiaries,
        list_my_transfers,
        get_my_transfer_status,
        cancel_my_transfer,
        list_my_topups,
        get_my_topup_status,
    ]
