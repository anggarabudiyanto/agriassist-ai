import faiss
from uuid import uuid4
from typing import List

import fitz  # PyMuPDF
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def create_vector_store(embeddings: GoogleGenerativeAIEmbeddings) -> FAISS:
    """Buat FAISS vector store kosong."""
    dim = len(embeddings.embed_query("hello"))
    index = faiss.IndexFlatL2(dim)
    return FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )


def add_pdf_to_store(vector_store: FAISS, pdf_bytes: bytes) -> int:
    """
    Parse PDF dari bytes, split jadi chunks, tambah ke vector store.
    Return jumlah chunks yang ditambahkan.
    """
    # Buka PDF dari bytes (bukan dari file path)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])

    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_text(text)

    if not chunks:
        return 0

    documents = [Document(page_content=chunk) for chunk in chunks]
    uuids = [str(uuid4()) for _ in documents]
    vector_store.add_documents(documents=documents, ids=uuids)

    return len(chunks)


def rag_search(vector_store: FAISS, query: str, k: int = 4) -> str:
    """Cari dokumen relevan, return sebagai string context."""
    docs = vector_store.similarity_search(query, k=k)
    if not docs:
        return "Tidak ada dokumen relevan ditemukan."
    return "\n\n".join(doc.page_content for doc in docs)
