from langchain_chroma import Chroma
from pathlib import Path

from . import KNOWLEDGE_ROUTES
from .embeddings import create_embedding_model
from .document_loader import load_knowledge_documents
from .text_splitter import split_knowledge_documents


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PERSIST_DIRECTORY = PROJECT_ROOT / "data" / "vector_store"


def create_vector_store(
        persist_directory: Path = DEFAULT_PERSIST_DIRECTORY,
) -> Chroma:
    embeddings = create_embedding_model()
    chroma = Chroma(
        collection_name="bank_knowledge",
        embedding_function=embeddings,
        persist_directory=str(persist_directory),
    )
    return chroma

def index_knowledge_documents(
        knowledge_base_path: Path,
        route: str,
        vector_store: Chroma | None = None,
) -> Chroma:
    documents = load_knowledge_documents(
        knowledge_base_path=knowledge_base_path,
        route=route
    )
    chunks = split_knowledge_documents(
        documents=documents
    )
    chunk_ids = [
        chunk.metadata["chunk_id"] for chunk in chunks
    ]
    vector_store = vector_store or create_vector_store()
    existing = vector_store.get(where={"route": route})
    existing_ids = set(existing["ids"])
    vector_store.add_documents(
        documents=chunks,
        ids=chunk_ids
    )
    stale_ids = existing_ids - set(chunk_ids)
    if stale_ids:
        vector_store.delete(ids=sorted(stale_ids))
    return vector_store



if __name__ == "__main__":
    knowledge_base_path = PROJECT_ROOT / "data" / "knowledge_base"
    vector_store = create_vector_store()
    for route in KNOWLEDGE_ROUTES:
        index_knowledge_documents(
            knowledge_base_path=knowledge_base_path,
            route=route,
            vector_store=vector_store,
        )

    stored_data = vector_store.get()
    print(f"Stored chunks: {len(stored_data['ids'])}")
