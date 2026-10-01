from langchain_groq import ChatGroq
from dotenv import load_dotenv


def create_chat_model():
    load_dotenv()
    return ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        max_retries=2
    )