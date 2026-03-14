"""
app.py — Streamlit web app for the Fitch Voice Agent.
"""

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

try:
    for _k, _v in st.secrets.items():
        os.environ.setdefault(_k, str(_v))
except Exception:
    pass

st.set_page_config(
    page_title="Fitch Voice Agent · Federico Canepa",
    page_icon="🎙️",
    layout="wide",
)

# ── Design system ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Reset & base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Layout ── */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0a0a0a !important;
    border-right: 1px solid #1f1f1f;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0;
}
.sidebar-logo {
    padding: 24px 20px 16px;
    border-bottom: 1px solid #1f1f1f;
    margin-bottom: 8px;
}
.sidebar-section-title {
    font-size: 0.68em;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #444;
    padding: 16px 4px 8px;
}
.report-card {
    background: #111;
    border: 1px solid #1f1f1f;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
    transition: border-color 0.2s;
}
.report-card:hover { border-color: #333; }
.report-title {
    font-size: 0.8em;
    font-weight: 500;
    color: #ccc;
    line-height: 1.4;
    margin-bottom: 10px;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px !important;
    font-size: 0.8em !important;
    font-weight: 500 !important;
    padding: 5px 10px !important;
    transition: all 0.15s !important;
    border: 1px solid #2a2a2a !important;
    background: #161616 !important;
    color: #aaa !important;
}
.stButton > button:hover {
    border-color: #444 !important;
    color: #fff !important;
    background: #1e1e1e !important;
}
.stButton > button[kind="primary"] {
    background: #ff6b35 !important;
    border-color: #ff6b35 !important;
    color: #fff !important;
}
.btn-ask > .stButton > button {
    background: #1a1a2e !important;
    border-color: #3b3b6b !important;
    color: #a0a8ff !important;
}
.btn-ask > .stButton > button:hover {
    background: #22224a !important;
    border-color: #5555aa !important;
    color: #c0c8ff !important;
}

/* ── Toggle & slider ── */
[data-testid="stToggle"] { margin: 4px 0; }
.stSlider { padding: 4px 0; }
[data-testid="stSlider"] > div > div > div {
    background: #ff6b35 !important;
}

/* ── Chat area ── */
.chat-wrapper {
    max-width: 760px;
    margin: 0 auto;
    padding: 32px 24px 120px;
}

/* User message */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: transparent !important;
    flex-direction: row-reverse;
    gap: 12px;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) > div:last-child {
    background: #1c2a3a;
    border: 1px solid #1e3a5f;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    max-width: 80%;
    color: #d0e4ff;
    font-size: 0.95em;
    line-height: 1.6;
}

/* Assistant message */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: transparent !important;
    gap: 12px;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) > div:last-child {
    background: #111;
    border: 1px solid #1f1f1f;
    border-radius: 4px 18px 18px 18px;
    padding: 14px 18px;
    max-width: 85%;
    color: #e0e0e0;
    font-size: 0.95em;
    line-height: 1.7;
}

/* Avatar */
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    border-radius: 50% !important;
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    font-size: 0.9em !important;
    flex-shrink: 0;
}

/* ── Audio player ── */
audio {
    width: 100% !important;
    height: 36px !important;
    margin-top: 10px;
    border-radius: 8px;
    filter: invert(0.85) hue-rotate(180deg) brightness(0.9);
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: #0d0d0d !important;
    border-top: 1px solid #1a1a1a !important;
    padding: 16px 24px !important;
    position: fixed !important;
    bottom: 0;
    max-width: 760px;
    left: 50%;
    transform: translateX(-50%) translateX(160px); /* offset for sidebar */
    width: calc(100% - 360px);
    z-index: 999;
}
[data-testid="stChatInput"] textarea {
    background: #161616 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 12px !important;
    color: #e0e0e0 !important;
    font-size: 0.95em !important;
    padding: 12px 16px !important;
    resize: none !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #ff6b35 !important;
    box-shadow: 0 0 0 2px rgba(255,107,53,0.15) !important;
}

/* ── Info box ── */
[data-testid="stAlert"] {
    background: #0f1a2e !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 10px !important;
    color: #90b8e8 !important;
}

/* ── Select box ── */
[data-testid="stSelectbox"] > div > div {
    background: #111 !important;
    border: 1px solid #222 !important;
    border-radius: 8px !important;
    color: #ccc !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #ff6b35; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }

/* ── Banner ── */
#fitch-banner {
    background: #0d0d0d;
    border: 1px solid #1f1f1f;
    border-left: 3px solid #ff6b35;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 28px;
    transition: opacity 0.8s ease, max-height 0.6s ease;
    overflow: hidden;
}

/* ── Form ── */
[data-testid="stForm"] {
    background: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 10px;
    padding: 12px;
}
[data-testid="stTextInput"] input {
    background: #111 !important;
    border: 1px solid #222 !important;
    border-radius: 8px !important;
    color: #ccc !important;
    font-size: 0.85em !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=3600)
def get_elevenlabs_voices() -> list[dict]:
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
            pass

    try:
        import io
        from gtts import gTTS
        buf = io.BytesIO()
        gTTS(text=text, lang="en", slow=(speed < 0.85)).write_to_fp(buf)
        return buf.getvalue(), "gTTS"
    except Exception:
        return None, ""


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
if "focus_url" not in st.session_state:
    st.session_state.focus_url = None
if "show_banner" not in st.session_state:
    st.session_state.show_banner = True

with st.spinner(""):
    preload_reports()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:1.15em;font-weight:600;color:#fff;letter-spacing:-0.02em;">
            🎙️ Fitch Voice Agent
        </div>
        <div style="font-size:0.75em;color:#555;margin-top:4px;">
            by Federico Canepa · Powered by ElevenLabs
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Voice ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section-title">Voice</div>', unsafe_allow_html=True)

    voice_enabled = st.toggle("Enable voice output", value=True)

    if voice_enabled:
        voices = get_elevenlabs_voices()
        if voices:
            default_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
            voice_names = [v["name"] for v in voices]
            voice_ids   = [v["id"]   for v in voices]
            default_idx = next((i for i, vid in enumerate(voice_ids) if vid == default_id), 0)
            selected_name     = st.selectbox("Voice", voice_names, index=default_idx, label_visibility="collapsed")
            selected_voice_id = voice_ids[voice_names.index(selected_name)]
        else:
            selected_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
            st.caption("Using Google TTS fallback")

        speed = st.slider("Speed", min_value=0.7, max_value=1.5, value=1.0, step=0.05)
    else:
        selected_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        speed = 1.0

    # ── Reports ───────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section-title">Reports</div>', unsafe_allow_html=True)

    with st.form("add_report_form", clear_on_submit=True):
        url_input = st.text_input("URL", placeholder="https://www.fitchratings.com/research/…", label_visibility="collapsed")
        submitted = st.form_submit_button("＋ Add Report", use_container_width=True)

    if submitted and url_input.strip():
        with st.spinner("Indexing…"):
            try:
                from ingest import ingest_url
                count = ingest_url(url_input.strip())
                if count:
                    st.session_state.indexed_reports.append(url_input.strip())
                    st.success(f"Indexed {count} chunks.")
                else:
                    st.info("Already indexed.")
            except Exception as e:
                st.error(f"{e}")

    for r in st.session_state.indexed_reports:
        label = r.rstrip("/").split("/")[-1].replace("-", " ").title()
        st.markdown(f"""
        <div class="report-card">
            <div class="report-title">{label[:60]}</div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="btn-ask">', unsafe_allow_html=True)
            if st.button("💬 Ask", key=f"ask_{r}", use_container_width=True):
                st.session_state.focus_url = r
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<a href="{r}" target="_blank" style="text-decoration:none"><button style="width:100%;padding:5px 10px;border-radius:8px;border:1px solid #2a2a2a;background:#161616;color:#888;font-size:0.8em;cursor:pointer;font-family:Inter,sans-serif;font-weight:500;transition:all 0.15s">🔗 View</button></a>', unsafe_allow_html=True)


# ── Main area ─────────────────────────────────────────────────────────────────

st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

# ── Title row ─────────────────────────────────────────────────────────────────

tcol, bcol = st.columns([10, 1])
with tcol:
    st.markdown('<h2 style="font-weight:600;letter-spacing:-0.03em;color:#f0f0f0;margin:0;padding:8px 0 4px">Fitch Voice Agent</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#555;font-size:0.85em;margin:0 0 20px">Ask anything about Federico Canepa\'s Fitch Ratings Structured Finance Reports</p>', unsafe_allow_html=True)
with bcol:
    st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
    banner_label = "ℹ️" if not st.session_state.show_banner else "✕"
    if st.button(banner_label, key="banner_toggle"):
        st.session_state.show_banner = not st.session_state.show_banner
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── Info banner ───────────────────────────────────────────────────────────────

if st.session_state.show_banner:
    st.markdown("""
<div id="fitch-banner">
  <div style="font-size:0.82em;font-weight:600;color:#ff6b35;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:10px">About this app</div>
  <p style="color:#999;font-size:0.88em;line-height:1.7;margin:0 0 14px">
    An AI-powered voice research assistant built on
    <a href="https://www.fitchratings.com/search/?query=federico+canepa" target="_blank" style="color:#ff6b35;text-decoration:none">Fitch Ratings Structured Finance Reports</a>
    authored by <strong style="color:#ccc">Federico Canepa</strong>.
    Ask a question and get a spoken answer — powered by
    <a href="https://elevenlabs.io" target="_blank" style="color:#ff6b35;text-decoration:none">ElevenLabs TTS</a>
    (<code style="background:#1a1a1a;padding:1px 5px;border-radius:4px;font-size:0.9em">eleven_turbo_v2</code>)
    and <strong style="color:#ccc">Claude AI</strong>.
  </p>
  <div style="display:flex;gap:24px;flex-wrap:wrap">
    <div style="font-size:0.82em;color:#555">① Add or select a report in the sidebar</div>
    <div style="font-size:0.82em;color:#555">② Type your question below</div>
    <div style="font-size:0.82em;color:#555">③ Press ▶ Play to hear the answer</div>
  </div>
</div>

<script>
(function() {
    setTimeout(function() {
        var el = window.parent.document.getElementById('fitch-banner');
        if (el) {
            el.style.opacity = '0';
            el.style.maxHeight = '0';
            el.style.padding = '0';
            el.style.margin = '0';
            el.style.border = 'none';
        }
    }, 30000);
})();
</script>
""", unsafe_allow_html=True)

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("ANTHROPIC_API_KEY not set — add it in Streamlit Cloud → Settings → Secrets.", icon="🔑")

# ── Focus banner ──────────────────────────────────────────────────────────────

focus_url = st.session_state.focus_url
if focus_url:
    focus_label = focus_url.rstrip("/").split("/")[-1].replace("-", " ").title()
    fc1, fc2 = st.columns([5, 1])
    with fc1:
        st.markdown(f'<div style="background:#0f1a2e;border:1px solid #1e3a5f;border-radius:8px;padding:8px 14px;font-size:0.82em;color:#6fa8dc">📄 Focused on: <strong>{focus_label[:55]}</strong></div>', unsafe_allow_html=True)
    with fc2:
        if st.button("✕ All reports", key="clear_focus"):
            st.session_state.focus_url = None
            st.rerun()

# ── Chat history ──────────────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🎙️"):
        st.markdown(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")

# ── Chat input ────────────────────────────────────────────────────────────────

if query := st.chat_input("Ask a question about the reports…"):
    active_focus = st.session_state.focus_url
    st.session_state.focus_url = None

    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="👤"):
        st.markdown(query)

    with st.chat_message("assistant", avatar="🎙️"):
        with st.spinner(""):
            try:
                from agent import answer
                response = answer(query, url_filter=active_focus)
            except Exception as e:
                response = f"Error: {e}"

        st.markdown(response)

        audio_bytes = None
        if voice_enabled:
            with st.spinner(""):
                audio_bytes, audio_source = generate_audio(response, selected_voice_id, speed)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
                st.markdown(f'<div style="font-size:0.72em;color:#444;margin-top:4px">▶ Press play · via {audio_source}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "audio": audio_bytes,
    })

st.markdown('</div>', unsafe_allow_html=True)
