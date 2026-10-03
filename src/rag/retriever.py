from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever


def create_bank_knowledge_retriever(
        vector_store: Chroma,
        route: str,
        k: int = 3,
) -> VectorStoreRetriever:
    if not isinstance(route, str):
        raise TypeError("Route must be a string")
    if not route.strip():
        raise ValueError("Route is empty")

    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("k must be an integer")
    if not 1 <= k <= 10:
        raise ValueError("k must be between 1 and 10")

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k,
            "filter": {"route": route.strip()},
        },
    )
