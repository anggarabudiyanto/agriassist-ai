import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Inisialisasi Gemini embeddings dari env."""
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
    )
