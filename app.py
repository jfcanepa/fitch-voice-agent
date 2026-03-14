"""
app.py — Streamlit web app for the Fitch Voice Agent.
"""

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Push Streamlit Cloud secrets into os.environ so all modules see them via os.getenv()
for _k, _v in st.secrets.items():
    os.environ.setdefault(_k, str(_v))

st.set_page_config(
    page_title="Fitch Voice Agent",
    page_icon="📊",
    layout="centered",
)


# ── Audio helper ──────────────────────────────────────────────────────────────

def _generate_audio(text: str) -> bytes | None:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return None
    try:
        from elevenlabs import ElevenLabs
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        client = ElevenLabs(api_key=api_key)
        chunks = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_turbo_v2",
            output_format="mp3_44100_128",
        )
        return b"".join(chunks)
    except Exception as e:
        return None


# ── Styles ────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .stChatMessage { border-radius: 12px; }
    .block-container { max-width: 780px; padding-top: 2rem; }
    .stTextInput > div > div > input { border-radius: 8px; }
    .stButton > button { border-radius: 8px; font-weight: 600; }
    .report-pill {
        display: inline-block;
        background: #313244;
        color: #cdd6f4;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8em;
        margin: 2px 2px;
    }
</style>
""", unsafe_allow_html=True)

# ── Default reports (pre-loaded for testers) ──────────────────────────────────

DEFAULT_REPORTS = [
    "https://www.fitchratings.com/research/structured-finance/fitch-takes-various-rating-actions-on-36-ffelp-slabs-29-01-2026",
]


@st.cache_resource(show_spinner=False)
def preload_reports():
    """Ingest default reports once per app session (cached so it only runs once)."""
    from ingest import ingest_url, get_collection
    collection = get_collection()
    loaded = []
    if collection.count() == 0:
        for url in DEFAULT_REPORTS:
            try:
                ingest_url(url)
                loaded.append(url)
            except Exception:
                pass
    return loaded


# ── Session state ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_reports" not in st.session_state:
    st.session_state.indexed_reports = list(DEFAULT_REPORTS)

with st.spinner("Loading reports…"):
    preload_reports()

# ── Header ────────────────────────────────────────────────────────────────────

st.title("📊 Fitch Voice Agent")
st.caption("Ask questions about your Fitch Ratings structured finance reports.")

# ── Sidebar — report management ───────────────────────────────────────────────

with st.sidebar:
    st.header("Reports")

    with st.form("add_report_form", clear_on_submit=True):
        url = st.text_input(
            "Fitch report URL",
            placeholder="https://www.fitchratings.com/research/...",
        )
        submitted = st.form_submit_button("Add Report", use_container_width=True)

    if submitted and url.strip():
        with st.spinner("Fetching and indexing report…"):
            try:
                from ingest import ingest_url
                count = ingest_url(url.strip())
                if count:
                    st.session_state.indexed_reports.append(url.strip())
                    st.success(f"Indexed {count} chunks.")
                else:
                    st.info("Already indexed.")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    if st.session_state.indexed_reports:
        st.markdown("**Indexed reports:**")
        for r in st.session_state.indexed_reports:
            label = r.rstrip("/").split("/")[-1].replace("-", " ").title()[:40]
            st.markdown(f'<span class="report-pill">📄 {label}</span>', unsafe_allow_html=True)
    else:
        st.info("No reports indexed yet. Add one above to get started.")

    st.divider()
    voice_enabled = st.toggle("Play voice response", value=True)
    if voice_enabled and not os.getenv("ELEVENLABS_API_KEY"):
        st.caption("⚠️ ELEVENLABS_API_KEY not set — voice disabled.")

# ── Chat history ──────────────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "📊"):
        st.markdown(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3", autoplay=False)

# ── Chat input ────────────────────────────────────────────────────────────────

if query := st.chat_input("Ask a question about your reports…"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(query)

    with st.chat_message("assistant", avatar="📊"):
        with st.spinner("Thinking…"):
            try:
                from agent import answer
                response = answer(query)
            except Exception as e:
                response = f"Error: {e}"

        st.markdown(response)

        audio_bytes = None
        if voice_enabled:
            audio_bytes = _generate_audio(response)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "audio": audio_bytes,
    })
