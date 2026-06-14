import os
from typing import Literal

from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from rag.vector_store import rag_search
from tools.web_search import web_search
from db.database import list_tables, describe_table, execute_query


# ─── SYSTEM PROMPT ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Kamu adalah AgriAssist AI, asisten pertanian cerdas berbahasa Indonesia.

Kamu memiliki akses ke 3 sumber informasi:

1. **RAG (Basis Pengetahuan PDF)** — untuk pertanyaan tentang:
   - Cara budidaya tanaman, teknik pertanian, proses tanam
   - Penjelasan penyakit/hama, gejala, dan cara penanganan
   - Informasi dari dokumen PDF yang diunggah user

2. **SQL DATABASE** — untuk pertanyaan tentang:
   - Harga pupuk (tabel: pupuk)
   - Daftar obat pertanian dan fungsinya (tabel: obat_pertanian)
   - Informasi hama dan penanganan terstruktur (tabel: hama_penyakit)

3. **WEB SEARCH** — untuk pertanyaan tentang:
   - Harga terbaru / hari ini
   - Berita pertanian terkini
   - Informasi cuaca atau update real-time

Selalu jawab dalam Bahasa Indonesia yang jelas dan ramah.
Jika informasi tidak tersedia di sumber manapun, katakan dengan jujur.
"""

ROUTER_PROMPT = """Kamu adalah classifier intent untuk sistem AI pertanian.

Klasifikasikan pertanyaan berikut ke dalam SATU kategori saja:
- RAG → pertanyaan tentang cara, proses, teknik, budidaya, penjelasan penyakit/hama
- SQL → pertanyaan tentang harga, daftar produk, stok, nama pupuk/obat dari database
- WEB → pertanyaan tentang informasi terbaru, harga hari ini, berita, cuaca, update

Balas HANYA dengan satu kata: RAG, SQL, atau WEB.

Pertanyaan: {question}
"""


# ─── ROUTER ───────────────────────────────────────────────────────────────────

def classify_intent(question: str, model) -> Literal["RAG", "SQL", "WEB"]:
    """Gunakan LLM untuk tentukan route yang tepat."""
    prompt = ROUTER_PROMPT.format(question=question)
    response = model.invoke(prompt)
    route = response.content.strip().upper()
    if route not in ("RAG", "SQL", "WEB"):
        return "RAG"  # fallback
    return route


# ─── SQL EXECUTOR (via LLM) ───────────────────────────────────────────────────

SQL_PROMPT = """Kamu adalah expert SQL untuk database pertanian SQLite.

Tabel yang tersedia:
- pupuk (pupuk_id, nama_pupuk, harga, fungsi)
- obat_pertanian (obat_id, nama_obat, kategori, harga, kegunaan)
- hama_penyakit (hama_id, nama_hama, gejala, penanganan)

Tugas kamu: Buat query SQL SELECT yang sesuai untuk menjawab pertanyaan berikut.
Balas HANYA dengan query SQL saja, tanpa penjelasan, tanpa markdown.

Pertanyaan: {question}
"""

def answer_via_sql(question: str, model) -> str:
    """Generate SQL query via LLM, eksekusi, format hasilnya."""
    # Generate SQL
    sql_prompt = SQL_PROMPT.format(question=question)
    sql_response = model.invoke(sql_prompt)
    sql = sql_response.content.strip().replace("```sql", "").replace("```", "").strip()

    # Eksekusi
    rows = execute_query(sql)

    if not rows:
        return "Data tidak ditemukan di database."

    # Format hasil ke teks yang mudah dibaca
    result_text = f"Query: {sql}\n\nHasil:\n"
    for row in rows:
        result_text += " | ".join(str(x) for x in row) + "\n"

    # Minta LLM rangkum hasilnya
    summary_prompt = f"""Rangkum hasil query database berikut dalam bahasa Indonesia yang ramah:

{result_text}

Pertanyaan asal: {question}

Berikan jawaban yang natural, bukan output mentah database."""

    summary = model.invoke(summary_prompt)
    return summary.content


# ─── RAG ANSWERER ─────────────────────────────────────────────────────────────

RAG_ANSWER_PROMPT = """Kamu adalah asisten pertanian AgriAssist.
Gunakan konteks berikut untuk menjawab pertanyaan. Jawab dalam Bahasa Indonesia.
Jika konteks tidak relevan, katakan bahwa informasi tidak tersedia di dokumen.

Konteks dari basis pengetahuan:
{context}

Pertanyaan: {question}

Jawaban:"""


def answer_via_rag(question: str, vector_store: FAISS, model) -> str:
    """Cari di vector store, jawab dengan LLM."""
    context = rag_search(vector_store, question)
    prompt = RAG_ANSWER_PROMPT.format(context=context, question=question)
    response = model.invoke(prompt)
    return response.content


# ─── MAIN AGENT ───────────────────────────────────────────────────────────────

def run_agent(
    question: str,
    vector_store: FAISS,
    llm_provider: str = "groq",
) -> tuple[str, str]:
    """
    Koordinator utama AgriAssist.

    Returns:
        (answer, route_used) — jawaban dan route yang dipakai (RAG/SQL/WEB)
    """

    # Pilih model
    if llm_provider == "gemini":
        model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=os.environ.get("GOOGLE_API_KEY"),
            temperature=0,
        )
    else:  # groq (default)
        model = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.environ.get("GROQ_API_KEY"),
            temperature=0,
        )

    # 1. Classify intent
    route = classify_intent(question, model)

    # 2. Execute berdasarkan route
    if route == "WEB":
        answer = web_search(question)

    elif route == "SQL":
        answer = answer_via_sql(question, model)

    else:  # RAG
        answer = answer_via_rag(question, vector_store, model)

    return answer, route
