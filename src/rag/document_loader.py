from pathlib import Path
from langchain_core.documents import Document
import yaml

def load_knowledge_documents(
        knowledge_base_path: Path,
        route: str) -> list[Document]:
    folder_path = knowledge_base_path / route
    if not folder_path.is_dir():
        raise FileNotFoundError(
            f"The folder does not exist or is a file: {folder_path}."
            )
    documents = []
    required_fields = {
        "document_id",
        "title",
        "route",
        "topic",
        "country",
        "effective_date",
        "version",
        "source",
    }
    markdown_files = sorted(folder_path.glob("*.md"))
    if not markdown_files:
        raise ValueError(
            f"No Markdown documents found in: {folder_path}"
            )
    for f in markdown_files:
        text = f.read_text(encoding="utf-8")
        if not text.startswith("---"):
            raise ValueError(
                f"{f.name}: missing YAML front matter"
                )
        parts = text.split("---" , maxsplit=2)
        if len(parts) != 3:
            raise ValueError(
                f"{f.name}: YAML front matter is not closed"
                )
        yaml_text = parts[1].strip()
        markdown_body = parts[2].strip()
        if not markdown_body:
            raise ValueError(
                f"{f.name}: Markdown body is empty"
            )
        metadata = yaml.safe_load(yaml_text)

        if not isinstance(metadata, dict):
            raise ValueError(
                f"{f.name}: YAML metadata must be a dictionary"
                )
        missing_fields = required_fields - metadata.keys()
        if missing_fields:
            raise ValueError(
                f"{f.name}: missing metadata fields: "
                f"{sorted(missing_fields)}"
            )
        for field in required_fields:
            if metadata[field] is None or str(metadata[field]).strip() == "":
                raise ValueError(
                    f"{f.name}: metadata field '{field}' cannot be empty"
                )
        if metadata["route"] != route:
             raise ValueError(
                f"{f.name}: expected route '{route}', "
                f"but found '{metadata['route']}'"
            )
        metadata["document_id"] = str(metadata["document_id"])
        metadata["effective_date"] = str(metadata["effective_date"])
        metadata["version"] = str(metadata["version"])

        documents.append(Document(
            page_content=markdown_body,
            metadata=metadata
        ))
    return documents

if __name__ == "__main__":
    knowledge_base_path = Path(__file__).resolve().parent.parent.parent
    folder = knowledge_base_path / "data" / "knowledge_base"
    documents = load_knowledge_documents(folder , "transfers_and_topups")
    print(documents[0].page_content)
