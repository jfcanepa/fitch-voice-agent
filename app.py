"""
app.py — Streamlit web app for the Fitch Voice Agent.
"""

import io
import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Fitch Voice Agent",
    page_icon="📊",
    layout="centered",
)


# ── Audio helper ──────────────────────────────────────────────────────────────

def _generate_audio(text: str) -> bytes:
    from elevenlabs import ElevenLabs
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    chunks = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_turbo_v2",
        output_format="mp3_44100_128",
    )
    return b"".join(chunks)

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

# ── Session state ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_reports" not in st.session_state:
    st.session_state.indexed_reports = []

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

    # Show indexed reports
    if st.session_state.indexed_reports:
        st.markdown("**Indexed reports:**")
        for r in st.session_state.indexed_reports:
            label = r.rstrip("/").split("/")[-1].replace("-", " ").title()[:40]
            st.markdown(f'<span class="report-pill">📄 {label}</span>', unsafe_allow_html=True)
    else:
        st.info("No reports indexed yet. Add one above to get started.")

    st.divider()
    voice_enabled = st.toggle("Play voice response", value=True)
    st.caption("Uses ElevenLabs TTS to speak answers in your browser.")

# ── Chat history ──────────────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "📊"):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "audio" in msg and msg["audio"]:
            st.audio(msg["audio"], format="audio/mp3", autoplay=False)

# ── Chat input ────────────────────────────────────────────────────────────────

if query := st.chat_input("Ask a question about your reports…"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(query)

    # Generate answer
    with st.chat_message("assistant", avatar="📊"):
        with st.spinner("Thinking…"):
            try:
                from agent import answer
                response = answer(query)
            except Exception as e:
                response = f"Error: {e}"

        st.markdown(response)

        # Generate audio if voice enabled
        audio_bytes = None
        if voice_enabled and os.getenv("ELEVENLABS_API_KEY"):
            try:
                audio_bytes = _generate_audio(response)
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            except Exception as e:
                st.caption(f"Voice unavailable: {e}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "audio": audio_bytes,
    })

