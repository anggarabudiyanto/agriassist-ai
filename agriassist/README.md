# 🌾 AgriAssist AI

Chatbot pertanian cerdas dengan 3 sumber jawaban:
- 📚 **RAG** — basis pengetahuan dari PDF yang diupload user
- 🌐 **Web Search** — info terbaru via DuckDuckGo
- 🗄️ **SQL** — database harga pupuk, obat, dan hama

LLM Router (Gemini/Groq) otomatis memilih sumber yang tepat per pertanyaan.

## Struktur

```
agriassist/
├── app.py               ← entry point Streamlit
├── auth.py              ← sidebar API key + PDF upload
├── requirements.txt
│
├── agent/
│   └── coordinator.py   ← router + orchestrator utama
│
├── rag/
│   ├── embeddings.py    ← Gemini embeddings
│   └── vector_store.py  ← FAISS + PDF processor
│
├── tools/
│   └── web_search.py    ← DuckDuckGo search
│
└── db/
    └── database.py      ← SQLite init + query tools
```

## Cara Jalankan Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

Masukkan Google AI API Key dan GROQ API Key di sidebar.

## Deploy ke Streamlit Cloud

1. Push ke GitHub
2. Buka share.streamlit.io → New app → pilih repo ini
3. Main file path: `app.py`
4. Tidak perlu Secrets — API key diinput langsung oleh user di sidebar

## Contoh Pertanyaan

| Pertanyaan | Route |
|---|---|
| "Bagaimana cara menanam padi?" | 📚 RAG |
| "Berapa harga pupuk Urea?" | 🗄️ SQL |
| "Harga gabah hari ini" | 🌐 Web |
| "Obat untuk wereng coklat apa?" | 🗄️ SQL |
| "Gejala penyakit blas pada padi" | 📚 RAG |
