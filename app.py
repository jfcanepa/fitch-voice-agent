"""
app.py — Streamlit web app for the Fitch Voice Agent.
"""

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Push Streamlit Cloud secrets into os.environ so all modules see them via os.getenv()
try:
    for _k, _v in st.secrets.items():
        os.environ.setdefault(_k, str(_v))
except Exception:
    pass

st.set_page_config(
    page_title="Fitch Voice Agent",
    page_icon="📊",
    layout="centered",
)

# ── Autoplay shim — browsers block autoplay without user interaction;
#    this JS trick works by resuming AudioContext on first click. ─────────────
st.markdown("""
<script>
window._playAudio = function() {
    const audios = window.parent.document.querySelectorAll('audio');
    if (audios.length > 0) {
        const last = audios[audios.length - 1];
        last.play().catch(() => {});
    }
};
</script>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=3600)
def get_elevenlabs_voices() -> list[dict]:
    """Fetch available ElevenLabs voices. Returns list of {id, name, category}."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return []
    try:
        from elevenlabs import ElevenLabs
        client = ElevenLabs(api_key=api_key)
        response = client.voices.get_all()
        voices = [
            {"id": v.voice_id, "name": v.name, "category": getattr(v, "category", "other")}
            for v in response.voices
        ]
        return sorted(voices, key=lambda v: v["name"])
    except Exception:
        return []


def generate_audio(text: str, voice_id: str, speed: float = 1.0) -> tuple[bytes | None, str]:
    """Try ElevenLabs first, fall back to gTTS. Returns (audio_bytes, source_label)."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if api_key:
        try:
            from elevenlabs import ElevenLabs, VoiceSettings
            client = ElevenLabs(api_key=api_key)
            chunks = client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_turbo_v2",
                output_format="mp3_44100_128",
                voice_settings=VoiceSettings(speed=speed),
            )
            return b"".join(chunks), "ElevenLabs"
        except Exception:
            pass  # fall through to gTTS

    # Free fallback: Google TTS
    try:
        import io
        from gtts import gTTS
        buf = io.BytesIO()
        gTTS(text=text, lang="en", slow=(speed < 0.85)).write_to_fp(buf)
        return buf.getvalue(), "gTTS"
    except Exception:
        return None, ""


# ── Styles ────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .stChatMessage { border-radius: 12px; }
    .block-container { max-width: 780px; padding-top: 2rem; }
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
    /* Make the audio player wider and more visible */
    audio { width: 100% !important; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Default reports ───────────────────────────────────────────────────────────

DEFAULT_REPORTS = [
    "https://www.fitchratings.com/research/structured-finance/fitch-takes-various-rating-actions-on-36-ffelp-slabs-29-01-2026",
    "https://www.fitchratings.com/research/structured-finance/fitch-takes-various-actions-on-three-ffelp-abs-trusts-03-03-2026",
    "https://www.fitchratings.com/research/es/structured-finance/fitch-withdraws-agsacb08-rating-after-early-amortization-12-03-2026",
    "https://www.fitchratings.com/research/es/structured-finance/fitch-affirms-withdraws-unagras-servicer-rating-at-aafc3-mex-19-02-2026",
    "https://www.fitchratings.com/research/es/structured-finance/fitch-affirms-abbe-leasings-rating-as-servicer-20-01-2026",
]


@st.cache_resource(show_spinner=False)
def preload_reports():
    from ingest import ingest_url, get_collection
    collection = get_collection()
    if collection.count() == 0:
        for url in DEFAULT_REPORTS:
            try:
                ingest_url(url)
            except Exception:
                pass


# ── Session state ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_reports" not in st.session_state:
    st.session_state.indexed_reports = list(DEFAULT_REPORTS)

with st.spinner("Loading reports…"):
    preload_reports()

# ── Header ────────────────────────────────────────────────────────────────────

st.title("📊 Fitch Voice Agent")

st.markdown("""
<div style="background:#181825;border-left:4px solid #89b4fa;border-radius:8px;padding:16px 20px;margin-bottom:1rem;">

<strong style="color:#89b4fa;font-size:1.05em;">What is this?</strong><br><br>
<span style="color:#cdd6f4;">
This is an AI-powered voice research assistant built on top of published
<a href="https://www.fitchratings.com/search/?query=federico+canepa" target="_blank" style="color:#89b4fa;">Fitch Ratings structured finance reports</a>
authored by <strong>Federico Canepa</strong>. Ask any question about the reports and get an answer
— read on screen and spoken aloud.
</span>

<br><br>
<strong style="color:#f5c2e7;font-size:1.02em;">🎙️ Powered by ElevenLabs</strong><br><br>
<span style="color:#cdd6f4;">
Voice output is generated in real time using the
<a href="https://elevenlabs.io" target="_blank" style="color:#f5c2e7;">ElevenLabs Text-to-Speech API</a>
(<code style="color:#f5c2e7;">eleven_turbo_v2</code> model) via the official Python SDK.
Each answer is converted to natural-sounding speech and streamed as an MP3 directly in the browser.
The sidebar lets you choose from all voices available on the account and adjust playback speed —
both controlled through the ElevenLabs <code style="color:#f5c2e7;">VoiceSettings</code> API.
</span>

<br><br>
<strong style="color:#a6e3a1;">How to use it:</strong>
<ol style="color:#cdd6f4;margin:8px 0 0 0;padding-left:1.2em;line-height:1.9em;">
  <li>The reports in the sidebar are pre-loaded — no setup needed.</li>
  <li>Type any question in the chat box (e.g. <em>"Which trusts were downgraded and why?"</em>).</li>
  <li>Claude AI retrieves the relevant report excerpts and writes a concise answer.</li>
  <li>ElevenLabs converts the answer to speech — press <strong>▶ Play</strong> to listen.</li>
  <li>Use <strong>Voice Settings</strong> in the sidebar to switch voice or change speed.</li>
</ol>
</div>
""", unsafe_allow_html=True)

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("ANTHROPIC_API_KEY is not set. Add it in Streamlit Cloud → Settings → Secrets.", icon="🔑")

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:

    # ── Voice settings ────────────────────────────────────────────────────────
    st.header("🎙️ Voice Settings")

    voice_enabled = st.toggle("Enable voice", value=True)

    if voice_enabled:
        voices = get_elevenlabs_voices()

        if voices:
            default_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
            voice_names = [v["name"] for v in voices]
            voice_ids   = [v["id"]   for v in voices]
            default_idx = next((i for i, vid in enumerate(voice_ids) if vid == default_id), 0)

            selected_name = st.selectbox("ElevenLabs Voice", voice_names, index=default_idx)
            selected_voice_id = voice_ids[voice_names.index(selected_name)]
        else:
            selected_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
            st.caption("ElevenLabs unavailable on this network — using Google TTS fallback.")

        speed = st.slider("Speed", min_value=0.7, max_value=1.5, value=1.0, step=0.05,
                          help="Playback speed of the generated audio")

        st.caption("▶ Press **Play** on the audio player after each answer.")
    else:
        selected_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        speed = 1.0

    st.divider()

    # ── Reports ───────────────────────────────────────────────────────────────
    st.header("📄 Reports")

    with st.form("add_report_form", clear_on_submit=True):
        url_input = st.text_input(
            "Fitch report URL",
            placeholder="https://www.fitchratings.com/research/...",
        )
        submitted = st.form_submit_button("Add Report", use_container_width=True)

    if submitted and url_input.strip():
        with st.spinner("Fetching and indexing…"):
            try:
                from ingest import ingest_url
                count = ingest_url(url_input.strip())
                if count:
                    st.session_state.indexed_reports.append(url_input.strip())
                    st.success(f"Indexed {count} chunks.")
                else:
                    st.info("Already indexed.")
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.indexed_reports:
        for r in st.session_state.indexed_reports:
            label = r.rstrip("/").split("/")[-1].replace("-", " ").title()[:38]
            st.markdown(f'<a href="{r}" target="_blank" class="report-pill">📄 {label}</a>', unsafe_allow_html=True)
    else:
        st.info("No reports yet. Add one above.")

# ── Chat history ──────────────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "📊"):
        st.markdown(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")

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
            with st.spinner("Generating audio…"):
                audio_bytes, audio_source = generate_audio(response, selected_voice_id, speed)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
                st.caption(f"▶ Press play to hear the answer · via {audio_source}")
            else:
                st.caption("⚠️ Could not generate audio.")

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "audio": audio_bytes,
    })
