import os
import streamlit as st
from rag.embeddings import get_embeddings
from rag.vector_store import create_vector_store


def auth_sidebar():
    """
    Sidebar untuk input API key dan pengaturan.

    Returns:
        (llm_provider, vector_store, reset_clicked)
        atau st.stop() jika belum login.
    """
    with st.sidebar:
        st.header("⚙️ Pengaturan")

        # ── API KEYS ──────────────────────────────────────
        st.subheader("🔑 API Keys")
        google_api_key = st.text_input("Google AI API Key", type="password")
        groq_api_key = st.text_input("GROQ API Key", type="password")

        # ── PILIH MODEL ───────────────────────────────────
        st.subheader("🤖 Model LLM")
        llm_provider = st.radio(
            "Gunakan model:",
            options=["groq", "gemini"],
            format_func=lambda x: "🚀 Groq (Llama 3.3)" if x == "groq" else "✨ Gemini Flash",
            horizontal=True,
        )

        # ── UPLOAD PDF ────────────────────────────────────
        st.subheader("📄 Upload PDF (opsional)")
        uploaded_pdf = st.file_uploader(
            "Upload dokumen pertanian",
            type=["pdf"],
            help="PDF akan diproses dan masuk ke basis pengetahuan RAG"
        )

        st.divider()

        # ── TOMBOL ────────────────────────────────────────
        reset_clicked = st.button("🔄 Reset Percakapan", use_container_width=True)
        enter_clicked = False

        if google_api_key and groq_api_key:
            enter_clicked = st.button("🚀 Mulai / Terapkan", type="primary", use_container_width=True)

    # ── VALIDASI ──────────────────────────────────────────
    if not google_api_key or not groq_api_key:
        st.info("👈 Masukkan Google AI API Key dan GROQ API Key di sidebar untuk memulai.", icon="🗝️")
        st.stop()

    if not enter_clicked and "vector_store" not in st.session_state:
        st.warning("Klik **Mulai / Terapkan** untuk mengaktifkan AgriAssist.", icon="⚠️")
        st.stop()

    # ── SET ENVIRONMENT ───────────────────────────────────
    os.environ["GOOGLE_API_KEY"] = google_api_key
    os.environ["GROQ_API_KEY"] = groq_api_key
    st.session_state["GOOGLE_API_KEY"] = google_api_key
    st.session_state["GROQ_API_KEY"] = groq_api_key

    # ── INIT VECTOR STORE (cache per session) ────────────
    if "vector_store" not in st.session_state or enter_clicked:
        with st.spinner("Menyiapkan basis pengetahuan..."):
            embeddings = get_embeddings()
            vector_store = create_vector_store(embeddings)
            st.session_state["vector_store"] = vector_store
            st.session_state["embeddings"] = embeddings

    # ── PROSES PDF YANG DIUPLOAD ──────────────────────────
    if uploaded_pdf is not None:
        pdf_key = f"pdf_{uploaded_pdf.name}"
        if pdf_key not in st.session_state:
            from rag.vector_store import add_pdf_to_store
            with st.spinner(f"Memproses {uploaded_pdf.name}..."):
                n_chunks = add_pdf_to_store(
                    st.session_state["vector_store"],
                    uploaded_pdf.read(),
                )
            st.session_state[pdf_key] = True
            st.sidebar.success(f"✅ {uploaded_pdf.name} ({n_chunks} chunks)")

    return llm_provider, st.session_state["vector_store"], reset_clicked
