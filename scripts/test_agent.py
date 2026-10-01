from src.llm.model_factory import create_chat_model
from src.agents.agent_factory import create_agents


model = create_chat_model()
agents = create_agents(model=model)

result = agents["general_agent"].invoke({
    "messages": [
        {
            "role": "user",
            "content": "Hello What can you help me with?"
        }
    ]
})

print(result["messages"][-1].content)