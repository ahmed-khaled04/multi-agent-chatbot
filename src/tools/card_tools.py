from langchain.tools import tool

from src.bank.database import block_card, get_card_status, list_customer_cards

def create_card_tools(customer_id: str):
    @tool
    def get_my_card_status(card_id: str) -> dict[str , object]:
        """ Get the  status and masked details of one of the
            customer's cards."""
        card = get_card_status(
            customer_id=customer_id,
            card_id=card_id
        )
        if card is None:
            return {
                "found": False,
                "message": "No matching card was found for this customer",
            }
        return {
            "found": True,
            "card": card
        }
    @tool
    def list_my_cards() -> list[dict[str , object]]:
        """List the customer's cards with masked details and current statuses."""
        cards = list_customer_cards(
            customer_id=customer_id
        )
        return cards

    @tool
    def block_my_card(card_id: str) -> dict[str, object]:
        """Block a stolen or compromised card after an explicit user request."""
        result = block_card(
            customer_id=customer_id,
            card_id=card_id
        )
        if result is None:
            return {
                "found": False,
                "message": "No matching card was found for this customer."
            }
        return {
            "found": True,
            "message": result
        }

    return [get_my_card_status, list_my_cards, block_my_card]
