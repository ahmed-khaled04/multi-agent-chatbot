from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pathlib import Path

from .document_loader import load_knowledge_documents

def split_knowledge_documents(
        documents: list[Document],
        chunk_size: int=1000,
        chunk_overlap: int=150
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n" , "\n" , " " , ""]
    )
    chunks = splitter.split_documents(documents)
    chunk_counts: dict[str, int] = {}
    for chunk in chunks:
        document_id = chunk.metadata["document_id"]
        chunk_index = chunk_counts.get(document_id, 0)
        chunk.metadata["chunk_id"] = f"{document_id}_chunk_{chunk_index}"
        chunk.metadata["chunk_index"] = chunk_index
        chunk_counts[document_id] = chunk_index + 1

    return chunks


if __name__ == "__main__":
    knowledge_base_path = Path(__file__).resolve().parent.parent.parent
    folder = knowledge_base_path / "data" / "knowledge_base"
    documents = load_knowledge_documents(folder , "transfers_and_topups")
    print(documents[0].metadata)
    chunks = split_knowledge_documents(documents=documents)
    print("Content of first chunk:\n")
    print(chunks[0].page_content)
    print(f"num of chunks: {len(chunks)}")
