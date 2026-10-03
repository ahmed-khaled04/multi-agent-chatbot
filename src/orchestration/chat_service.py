from dataclasses import dataclass

from langchain_core.messages import HumanMessage

from src.routing.classifier import ClassifierRouter
from src.agents.agent_factory import create_agents
from src.llm.model_factory import create_chat_model
from src.orchestration.conversation_memory import ConversationMemory
from src.rag import KNOWLEDGE_ROUTES
from src.rag.context import KnowledgeContext, retrieve_knowledge_context
from src.rag.retriever import create_bank_knowledge_retriever
from src.rag.vector_store import create_vector_store

# tools
from src.tools.card_tools import create_card_tools
from src.tools.payment_tools import create_payment_tools
from src.tools.transfer_tools import create_transfer_tools
from src.tools.account_tools import create_account_tools


@dataclass(frozen=True)
class ChatResponse:
    reply: str
    route: str
    confidence: float


class ChatService():
    def __init__(self ,
                 customer_id: str,
                 max_history_turns: int = 5):
        self.customer_id = customer_id
        self.memory = ConversationMemory(max_turns=max_history_turns)
        self.router = ClassifierRouter()
        self.model = create_chat_model()
        self.vector_store = create_vector_store()
        self.knowledge_retrievers = {
            route: create_bank_knowledge_retriever(
                vector_store=self.vector_store,
                route=route,
            )
            for route in KNOWLEDGE_ROUTES
        }

        card_tools = create_card_tools(customer_id=self.customer_id)
        payment_tools = create_payment_tools(customer_id=self.customer_id)
        transfer_tools = create_transfer_tools(customer_id=self.customer_id)
        account_tools = create_account_tools(customer_id=self.customer_id)

        tools_by_route = {
            "card_services": card_tools,
            "payments_and_disputes": payment_tools,
            "transfers_and_topups": transfer_tools,
            "account_currency_and_access": account_tools
        }
        
        self.agents = create_agents(model=self.model,
                                    tools_by_route=tools_by_route)

    def respond(self , message: str) -> str:
        return self.respond_with_metadata(message).reply

    def respond_with_metadata(self, message: str) -> ChatResponse:
        prediction = self.router.predict_with_confidence(message=message)
        route = prediction.route
        agent = self.agents[route]
        current_message = HumanMessage(content=message)
        knowledge_context = ""
        retriever = self.knowledge_retrievers.get(route)
        if retriever is not None:
            knowledge_context = retrieve_knowledge_context(
                retriever=retriever,
                query=message,
            )

        result = agent.invoke({
            "messages": self.memory.messages_with(current_message)
        }, context=KnowledgeContext(knowledge_context=knowledge_context))
        final_message = result["messages"][-1]
        self.memory.add_turn(current_message, final_message)
        return ChatResponse(
            reply=final_message.content,
            route=route,
            confidence=prediction.confidence,
        )

    def clear_history(self) -> None:
        self.memory.clear()

# Test
if __name__ == "__main__":
    chat_service = ChatService(customer_id="cus_001")

    message = "What is the currencies available for my account"

    print(chat_service.router.predict(message=message))

    print(chat_service.respond(message=message))
