from langchain.agents import create_agent

from src.agents.prompts import SYSTEM_PROMPTS
from src.rag.context import (
    KnowledgeContext,
    create_knowledge_context_middleware,
)

def create_agents(
        model,
        tools_by_route=None
):
    tools_by_route = tools_by_route or {}
    agents = {}

    for route , system_prompt in SYSTEM_PROMPTS.items():
        route_tools = (
            []
            if route == "general_agent"
            else tools_by_route.get(route, [])
        )

        agents[route] = create_agent(model=model,
                                     tools=route_tools,
                                     system_prompt=system_prompt,
                                     middleware=[
                                         create_knowledge_context_middleware()
                                     ],
                                     context_schema=KnowledgeContext)
    return agents
