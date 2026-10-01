from langchain_core.messages import HumanMessage

from src.routing.classifier import ClassifierRouter
from src.agents.agent_factory import create_agents
from src.llm.model_factory import create_chat_model

# tools
from src.tools.card_tools import create_card_tools
from src.tools.payment_tools import create_payment_tools
from src.tools.transfer_tools import create_transfer_tools


class ChatService():
    def __init__(self ,
                 customer_id: str):
        self.customer_id = customer_id
        self.router = ClassifierRouter()
        self.model = create_chat_model()

        card_tools = create_card_tools(customer_id=self.customer_id)
        payment_tools = create_payment_tools(customer_id=self.customer_id)
        transfer_tools = create_transfer_tools(customer_id=self.customer_id)

        tools_by_route = {
            "card_services": card_tools,
            "payments_and_disputes": payment_tools,
            "transfers_and_topups": transfer_tools
        }
        
        self.agents = create_agents(model=self.model,
                                    tools_by_route=tools_by_route)

    def respond(self , message: str) -> str:
        route = self.router.predict(message=message)
        agent = self.agents[route]

        result = agent.invoke({
            "messages" : [
                HumanMessage(content=message)
            ]
        }) 
        final_message = result["messages"][-1]
        return final_message.content

# Test
if __name__ == "__main__":
    chat_service = ChatService(customer_id="cus_001")

    message = "What is the is the status of transfer trf_001."

    print(chat_service.router.predict(message=message))

    print(chat_service.respond(message=message))