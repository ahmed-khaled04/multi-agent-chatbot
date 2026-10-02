from langchain.tools import tool

from src.bank.database import (
    get_account_balance,
    get_account_details,
    get_exchange_rate,
    list_customer_accounts,
    list_supported_currencies,
    request_account_closure,
    request_profile_update,
)


def create_account_tools(customer_id: str):
    @tool
    def get_my_accounts() -> list[dict[str, object]]:
        """List all accounts owned by the customer.

        Use this when the customer asks what accounts they have or when an
        account ID is needed before calling another account-specific tool.
        Account numbers are returned only in masked form.
        """
        return list_customer_accounts(customer_id=customer_id)

    @tool
    def get_my_account_details(account_id: str) -> dict[str, object]:
        """Get status and masked details for one customer-owned account."""
        account = get_account_details(
            customer_id=customer_id,
            account_id=account_id,
        )
        if account is None:
            return {
                "found": False,
                "message": "No matching account was found for this customer.",
            }
        return {"found": True, "account": account}

    @tool
    def get_my_account_balance(account_id: str) -> dict[str, object]:
        """Get current and available balances for one customer-owned account."""
        balance = get_account_balance(
            customer_id=customer_id,
            account_id=account_id,
        )
        if balance is None:
            return {
                "found": False,
                "message": "No matching account was found for this customer.",
            }
        return {"found": True, "balance": balance}

    @tool
    def get_bank_supported_currencies() -> list[dict[str, object]]:
        """List currencies the bank currently supports holding or exchanging."""
        return list_supported_currencies()

    @tool
    def get_bank_exchange_rate(
        base_currency: str,
        quote_currency: str,
    ) -> dict[str, object]:
        """Get the current bank exchange rate between two currency codes.

        Pass three-letter codes such as EGP, USD, EUR, GBP, or JOD. The rate
        represents how much quote_currency equals one unit of base_currency.
        """
        try:
            rate = get_exchange_rate(
                base_currency=base_currency,
                quote_currency=quote_currency,
            )
        except ValueError as error:
            return {"found": False, "message": str(error)}

        if rate is None:
            return {
                "found": False,
                "message": "No current exchange rate was found for this pair.",
            }
        return {"found": True, "exchange_rate": rate}

    @tool
    def request_my_profile_update(
        field_name: str,
        new_value: str,
    ) -> dict[str, object]:
        """Request a personal-detail update after explicit customer confirmation.

        Allowed fields are full_name, email, country, phone_number, and
        preferred_language. This submits the change for review; it does not
        immediately change the customer's profile.
        """
        try:
            update_request = request_profile_update(
                customer_id=customer_id,
                field_name=field_name,
                new_value=new_value,
            )
        except ValueError as error:
            return {"success": False, "message": str(error)}

        if update_request is None:
            return {
                "success": False,
                "message": "The customer profile was not found.",
            }
        return {"success": True, "profile_update": update_request}

    @tool
    def request_my_account_closure(
        account_id: str,
        reason: str | None = None,
    ) -> dict[str, object]:
        """Request account closure after explicit customer confirmation.

        This creates a closure request for review and does not immediately
        close the account. An optional reason may be provided.
        """
        try:
            closure_request = request_account_closure(
                customer_id=customer_id,
                account_id=account_id,
                reason=reason,
            )
        except ValueError as error:
            return {"success": False, "message": str(error)}

        if closure_request is None:
            return {
                "success": False,
                "message": "No matching account was found for this customer.",
            }
        return {"success": True, "account_closure": closure_request}

    return [
        get_my_accounts,
        get_my_account_details,
        get_my_account_balance,
        get_bank_supported_currencies,
        get_bank_exchange_rate,
        request_my_profile_update,
        request_my_account_closure,
    ]
