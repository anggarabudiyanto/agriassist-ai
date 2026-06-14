import streamlit as st
from google.api_core.exceptions import ResourceExhausted

from auth import auth_sidebar
from agent.coordinator import run_agent
from db.database import init_db

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgriAssist AI",
    page_icon="🌾",
    layout="wide",
)

# ─── GLOBAL CSS + BACKGROUND ──────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Background pertanian ── */
[data-testid="stAppViewContainer"] {
    background-image:
        linear-gradient(rgba(10, 30, 10, 0.72), rgba(10, 30, 10, 0.72)),
        url("https://images.unsplash.com/photo-1500076656116-558758c991c1?w=1600&q=80");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Sidebar lebih gelap transparan */
[data-testid="stSidebar"] {
    background: rgba(10, 40, 10, 0.88) !important;
    border-right: 1px solid rgba(100, 200, 100, 0.2);
}
[data-testid="stSidebar"] * {
    color: #d4edda !important;
}
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.08) !important;
    color: #d4edda !important;
    border: 1px solid rgba(100,200,100,0.3) !important;
}

/* Teks utama terang */
html, body, [data-testid="stMarkdown"], .stMarkdown, p, span, label {
    color: #e8f5e9 !important;
}

/* Chat bubble user */
[data-testid="stChatMessageContent"] {
    background: rgba(20, 60, 20, 0.75) !important;
    border: 1px solid rgba(100,200,100,0.25) !important;
    border-radius: 12px !important;
    color: #e8f5e9 !important;
}

/* Input chat */
[data-testid="stChatInput"] textarea {
    background: rgba(10, 40, 10, 0.80) !important;
    color: #e8f5e9 !important;
    border: 1px solid rgba(100,200,100,0.4) !important;
    border-radius: 10px !important;
}

/* Info/warning/success box */
[data-testid="stAlert"] {
    background: rgba(20, 60, 20, 0.75) !important;
    border: 1px solid rgba(100,200,100,0.35) !important;
    color: #d4edda !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: rgba(20, 70, 20, 0.65) !important;
    border-radius: 10px;
    padding: 12px;
    border: 1px solid rgba(100,200,100,0.3);
}

/* Tombol primary */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2e7d32, #43a047) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #43a047, #66bb6a) !important;
}

/* Divider */
hr {
    border-color: rgba(100,200,100,0.25) !important;
}

/* Typing animation */
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0; }
}
.cursor {
    display: inline-block;
    width: 3px;
    height: 1.1em;
    background: #66bb6a;
    margin-left: 4px;
    vertical-align: text-bottom;
    animation: blink 0.8s infinite;
    border-radius: 2px;
}

/* Landing hero */
.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    color: #a5d6a7 !important;
    text-shadow: 0 2px 12px rgba(0,0,0,0.6);
    line-height: 1.15;
    margin-bottom: 0.2rem;
}
.hero-sub {
    font-size: 1.15rem;
    color: #c8e6c9 !important;
    margin-bottom: 1.5rem;
    letter-spacing: 0.04em;
}
.feature-card {
    background: rgba(20,70,20,0.60);
    border: 1px solid rgba(100,200,100,0.30);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.feature-card:hover {
    border-color: rgba(100,200,100,0.65);
}
.feature-icon { font-size: 1.8rem; }
.feature-title { font-weight: 700; color: #a5d6a7 !important; font-size: 1.05rem; }
.feature-desc  { color: #c8e6c9 !important; font-size: 0.9rem; margin-top: 2px; }

/* Badge route */
.route-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 4px;
}
.badge-rag { background: rgba(46,125,50,0.5);  border: 1px solid #66bb6a; color: #a5d6a7 !important; }
.badge-sql { background: rgba(21,101,192,0.5); border: 1px solid #64b5f6; color: #bbdefb !important; }
.badge-web { background: rgba(230,81,0,0.4);   border: 1px solid #ffb74d; color: #ffe0b2 !important; }
</style>
""", unsafe_allow_html=True)

# ─── INISIALISASI DB ──────────────────────────────────────────────────────────
init_db()

# ─── LANDING PAGE (sebelum login) ─────────────────────────────────────────────
def show_landing():
    """Halaman awal dengan animasi typing dan penjelasan fitur."""

    st.markdown("""
    <div style="text-align:center; padding: 2.5rem 0 1.5rem 0;">
        <div class="hero-title">🌾 AgriAssist AI</div>
        <div id="typing-target" class="hero-sub">
            Asisten Pertanian Cerdas Berbasis AI
            <span class="cursor"></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Typing animation via JS
    st.components.v1.html("""
    <script>
    const phrases = [
        "Asisten Pertanian Cerdas Berbasis AI",
        "Tanya tentang hama dan penyakit tanaman 🐛",
        "Cek harga pupuk terbaru 💰",
        "Upload PDF dokumen pertanian 📄",
        "Info cuaca & berita terkini 🌐"
    ];
    let pi = 0, ci = 0, deleting = false;

    function tick() {
        const el = window.parent.document.getElementById("typing-target");
        if (!el) { setTimeout(tick, 200); return; }

        // Hapus cursor span dulu agar tidak ikut terhapus
        const cursor = el.querySelector(".cursor");
        const text = cursor ? el.textContent : el.textContent;

        const full = phrases[pi];
        if (!deleting) {
            el.textContent = full.slice(0, ci + 1);
            ci++;
            if (ci === full.length) { deleting = true; setTimeout(tick, 1800); return; }
            setTimeout(tick, 55);
        } else {
            el.textContent = full.slice(0, ci - 1);
            ci--;
            if (ci === 0) {
                deleting = false;
                pi = (pi + 1) % phrases.length;
                setTimeout(tick, 400);
                return;
            }
            setTimeout(tick, 28);
        }

        // Reattach cursor
        const cur = document.createElement("span");
        cur.className = "cursor";
        el.appendChild(cur);
    }

    setTimeout(tick, 600);
    </script>
    """, height=0)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <div class="feature-title">RAG — Basis Pengetahuan</div>
            <div class="feature-desc">Upload PDF dokumen pertanian. AgriAssist akan membaca dan menjawab berdasarkan isinya secara akurat.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🗄️</div>
            <div class="feature-title">SQL — Database Produk</div>
            <div class="feature-desc">Data pupuk, obat pertanian, hama & penyakit tersimpan di database. Tanya harga atau daftar produk secara instan.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🌐</div>
            <div class="feature-title">Web Search — Info Terkini</div>
            <div class="feature-desc">Harga gabah hari ini, berita pertanian, cuaca — AgriAssist mencari langsung dari internet secara real-time.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Contoh pertanyaan
    st.markdown("""
    <div style="text-align:center; color:#a5d6a7; font-weight:700; font-size:1rem; margin-bottom:10px;">
        💬 Contoh pertanyaan yang bisa kamu tanyakan:
    </div>
    """, unsafe_allow_html=True)

    q_col1, q_col2 = st.columns(2)
    questions = [
        ("📚", "Bagaimana cara mengendalikan hama wereng?"),
        ("🗄️", "Berapa harga pupuk Urea sekarang?"),
        ("🌐", "Harga gabah terbaru hari ini"),
        ("📚", "Apa gejala penyakit blas pada padi?"),
        ("🗄️", "Obat apa untuk penyakit jamur pada tanaman?"),
        ("🌐", "Berita pertanian terkini di Indonesia"),
    ]
    for i, (icon, q) in enumerate(questions):
        col = q_col1 if i % 2 == 0 else q_col2
        col.markdown(f"""
        <div style="background:rgba(20,60,20,0.55); border:1px solid rgba(100,200,100,0.25);
                    border-radius:8px; padding:8px 14px; margin-bottom:8px; font-size:0.9rem; color:#c8e6c9;">
            {icon} {q}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-top:2rem; color:#81c784; font-size:0.95rem;">
        👈 Masukkan API Key di sidebar untuk memulai
    </div>
    """, unsafe_allow_html=True)


# ─── SIDEBAR AUTH ─────────────────────────────────────────────────────────────
# Tampilkan landing dulu sebelum auth selesai
if "vector_store" not in st.session_state:
    show_landing()

llm_provider, vector_store, reset_clicked = auth_sidebar()

# Kalau sudah login, clear landing dan tampilkan chat
st.empty()

# ─── HEADER CHAT ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <span style="font-size:2rem;">🌾</span>
    <div>
        <div style="font-size:1.6rem; font-weight:800; color:#a5d6a7;">AgriAssist AI</div>
        <div style="font-size:0.85rem; color:#81c784;">Chatbot Pertanian Cerdas — RAG · Web Search · SQL Database</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Badge sumber aktif
c1, c2, c3 = st.columns(3)
c1.markdown('<div class="route-badge badge-rag">📚 RAG — Dokumen PDF</div>', unsafe_allow_html=True)
c2.markdown('<div class="route-badge badge-web">🌐 Web Search — Terkini</div>', unsafe_allow_html=True)
c3.markdown('<div class="route-badge badge-sql">🗄️ SQL — Harga & Produk</div>', unsafe_allow_html=True)

st.divider()

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if reset_clicked:
    st.session_state.messages = []
    st.rerun()

# ─── RIWAYAT CHAT ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("route") and msg["route"] != "ERROR":
            badge = {"RAG": '<span class="route-badge badge-rag">📚 RAG</span>',
                     "SQL": '<span class="route-badge badge-sql">🗄️ SQL</span>',
                     "WEB": '<span class="route-badge badge-web">🌐 Web</span>'}
            st.markdown(badge.get(msg["route"], ""), unsafe_allow_html=True)

# ─── PESAN SAMBUTAN ───────────────────────────────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("""
Halo! Saya **AgriAssist AI** 🌾 — siap membantu pertanyaan seputar pertanian kamu.

Silakan tanyakan apa saja: hama, budidaya, harga pupuk, atau info terbaru!
        """)

# ─── INPUT USER ───────────────────────────────────────────────────────────────
user_input = st.chat_input("Tanyakan tentang pupuk, hama, cara tanam, harga...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Sedang mencari jawaban..."):
            try:
                answer, route = run_agent(
                    question=user_input,
                    vector_store=vector_store,
                    llm_provider=llm_provider,
                )
            except ResourceExhausted:
                answer = "⚠️ Kuota API habis. Silakan tunggu sebentar atau ganti API key."
                route = "ERROR"
            except Exception as e:
                answer = f"⚠️ Terjadi error: {str(e)}"
                route = "ERROR"

        st.markdown(answer)

        if route != "ERROR":
            badge = {"RAG": '<span class="route-badge badge-rag">📚 RAG</span>',
                     "SQL": '<span class="route-badge badge-sql">🗄️ SQL</span>',
                     "WEB": '<span class="route-badge badge-web">🌐 Web</span>'}
            st.markdown(badge.get(route, ""), unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "route": route,
    })
