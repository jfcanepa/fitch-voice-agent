"""
app.py — Streamlit web app for the Fitch Voice Agent.
UI inspired by ElevenLabs design system.
"""

import os
import re

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
    layout="centered",
)

# ── ElevenLabs-inspired design system ────────────────────────────────────────
# Palette: #FDFCFC bg · #FFFFFF cards · #E5E5E5 borders
# Accent:  #4056CE blue · #10B978 green · #3D3D3D secondary text
# Font:    Inter (body/UI) — matches ElevenLabs' UI font

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/*
 * Palette
 * Page bg:    #F2F2F2   (medium-light gray)
 * Sidebar bg: #E8E8E8
 * Cards:      #EBEBEB
 * Inputs:     #E4E4E4
 * Borders:    #D0D0D0
 * Text:       #111 primary · #555 secondary
 * Accent:     #4056CE blue
 */

/* ── Base ── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background-color: #F2F2F2 !important;
    color: #111 !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Main container ── */
.block-container {
    max-width: 740px !important;
    padding-top: 3rem !important;
    padding-bottom: 6rem !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #E8E8E8 !important;
    border-right: 1px solid #D0D0D0 !important;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 2rem !important;
    max-width: 100% !important;
}

/* All text in sidebar */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: #111 !important;
}

/* ── Typography ── */
h1, h2, h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #111 !important;
}
p, li { color: #444; }

/* ── Buttons — default ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78em !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
    text-transform: uppercase !important;
    border-radius: 6px !important;
    padding: 6px 14px !important;
    transition: all 0.15s ease !important;
    border: 1px solid #C0C0C0 !important;
    background: #DCDCDC !important;
    color: #333 !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    border-color: #4056CE !important;
    color: #4056CE !important;
    background: #D4D9F5 !important;
}

/* ── Add Report button ── */
[data-testid="stForm"] button[kind="secondaryFormSubmit"],
[data-testid="stForm"] .stButton > button {
    background: #CECECE !important;
    color: #222 !important;
    border-color: #B8B8B8 !important;
    width: 100% !important;
}
[data-testid="stForm"] button[kind="secondaryFormSubmit"]:hover,
[data-testid="stForm"] .stButton > button:hover {
    background: #D4D9F5 !important;
    border-color: #4056CE !important;
    color: #4056CE !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input {
    font-family: 'Inter', sans-serif !important;
    background: #E4E4E4 !important;
    border: 1px solid #C8C8C8 !important;
    border-radius: 8px !important;
    color: #111 !important;
    font-size: 0.9em !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #4056CE !important;
    box-shadow: 0 0 0 3px rgba(64,86,206,0.12) !important;
}

/* ── Chat input box ── */
[data-testid="stChatInput"] textarea {
    background: #E4E4E4 !important;
    border: 1px solid #C8C8C8 !important;
    border-radius: 8px !important;
    color: #111 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9em !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #111 !important;
    opacity: 1 !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #4056CE !important;
    box-shadow: 0 0 0 3px rgba(64,86,206,0.12) !important;
}

/* ── Bottom chat bar ── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
.stChatFloatingInputContainer,
.stChatFloatingInputContainer > div {
    background: #EBEBEB !important;
    border-top: 1px solid #D0D0D0 !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #E4E4E4 !important;
    border: 1px solid #C8C8C8 !important;
    border-radius: 8px !important;
    font-size: 0.88em !important;
    color: #111 !important;
}

/* ── Slider — track, thumb, label, value ── */
[data-testid="stSlider"] > div > div > div {
    background: #4056CE !important;
}
[data-testid="stSlider"] label,
[data-testid="stSlider"] p,
[data-testid="stSlider"] span,
[data-testid="stSlider"] div[data-testid="stTickBarMin"],
[data-testid="stSlider"] div[data-testid="stTickBarMax"] {
    color: #333 !important;
    font-size: 0.85em !important;
}

/* ── Toggle ── */
[data-testid="stToggle"] label,
[data-testid="stToggle"] p {
    font-size: 0.88em !important;
    color: #333 !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 4px 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
    background: #D8DDFA !important;
    border: 1px solid #BCC5F5 !important;
    border-radius: 16px 16px 4px 16px !important;
    padding: 12px 16px !important;
    font-size: 0.9em !important;
    color: #1a2a6c !important;
    max-width: 82% !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
    background: #ECECEC !important;
    border: 1px solid #D0D0D0 !important;
    border-radius: 4px 16px 16px 16px !important;
    padding: 14px 18px !important;
    font-size: 0.9em !important;
    color: #1a1a1a !important;
    max-width: 90% !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    width: 30px !important;
    height: 30px !important;
    min-width: 30px !important;
    font-size: 0.85em !important;
}

/* ── Audio ── */
audio { width: 100% !important; margin-top: 10px; border-radius: 6px; }

/* ── Form container ── */
[data-testid="stForm"] {
    background: #E2E2E2 !important;
    border: 1px solid #C8C8C8 !important;
    border-radius: 10px;
    padding: 12px;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: #DDE3FA !important;
    border: 1px solid #BCC5F5 !important;
    border-radius: 8px !important;
    color: #2c3ea0 !important;
    font-size: 0.85em !important;
}

/* ── Divider ── */
hr { border-color: #D0D0D0 !important; margin: 12px 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #FAFAFA; }
::-webkit-scrollbar-thumb { background: #E5E5E5; border-radius: 2px; }

/* ── Sidebar labels ── */
.section-label {
    font-size: 0.68em;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #777;
    margin: 20px 0 8px;
}

/* ── Report card ── */
.report-card {
    background: #DCDCDC;
    border: 1px solid #C8C8C8;
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 6px;
    font-size: 0.8em;
    color: #000 !important;
    line-height: 1.4;
    font-weight: 600;
}

/* ── Info banner ── */
.info-banner {
    background: #EBEBEB;
    border: 1px solid #D0D0D0;
    border-left: 3px solid #4056CE;
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 24px;
    transition: opacity 0.8s ease, max-height 0.6s ease, padding 0.4s ease;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


# ── Label helper ─────────────────────────────────────────────────────────────

_ACRONYMS = {"Ffelp", "Abs", "Slabs", "Sf", "Cdo", "Clo", "Rmbs", "Cmbs", "Abs"}

def label_from_url(url: str) -> str:
    """Convert a Fitch URL slug into a clean readable title."""
    slug = url.rstrip("/").split("/")[-1]
    # Strip trailing date pattern like -29-01-2026 or -03-03-2026
    slug = re.sub(r"-\d{2}-\d{2}-\d{4}$", "", slug)
    words = slug.replace("-", " ").title().split()
    # Restore known acronyms to uppercase
    fixed = []
    for w in words:
        if w in _ACRONYMS:
            fixed.append(w.upper())
        else:
            fixed.append(w)
    return " ".join(fixed)


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
        return sorted(
            [{"id": v.voice_id, "name": v.name} for v in response.voices],
            key=lambda v: v["name"],
        )
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


# ── Data ──────────────────────────────────────────────────────────────────────

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
    if get_collection().count() == 0:
        for url in DEFAULT_REPORTS:
            try:
                ingest_url(url)
            except Exception:
                pass


# ── Session state ─────────────────────────────────────────────────────────────

if "messages"        not in st.session_state: st.session_state.messages        = []
if "indexed_reports" not in st.session_state: st.session_state.indexed_reports = list(DEFAULT_REPORTS)
if "focus_url"       not in st.session_state: st.session_state.focus_url       = None
if "show_banner"     not in st.session_state: st.session_state.show_banner     = True

with st.spinner("Loading reports…"):
    preload_reports()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
        <div style="padding-bottom:16px;border-bottom:1px solid #C8C8C8">
            <div style="font-size:1.1em;font-weight:700;color:#111;letter-spacing:-0.02em">🎙️ Fitch Voice Agent</div>
            <div style="font-size:0.75em;color:#777;margin-top:3px">by Federico Canepa</div>
        </div>
    """, unsafe_allow_html=True)

    # Voice
    st.markdown('<div class="section-label">Voice</div>', unsafe_allow_html=True)
    voice_enabled = st.toggle("Enable voice output", value=True)

    if voice_enabled:
        voices = get_elevenlabs_voices()
        if voices:
            default_id  = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
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

    # Reports
    st.markdown('<div class="section-label">Reports</div>', unsafe_allow_html=True)

    with st.form("add_report_form", clear_on_submit=True):
        url_input = st.text_input("URL", placeholder="https://www.fitchratings.com/research/…", label_visibility="collapsed")
        if st.form_submit_button("＋ Add Report", use_container_width=True):
            if url_input.strip():
                with st.spinner("Indexing…"):
                    try:
                        from ingest import ingest_url
                        count = ingest_url(url_input.strip())
                        if count:
                            st.session_state.indexed_reports.append(url_input.strip())
                            st.success(f"Added — {count} chunks indexed.")
                        else:
                            st.info("Already indexed.")
                    except Exception as e:
                        st.error(str(e))

    for r in st.session_state.indexed_reports:
        label = label_from_url(r)
        st.markdown(f'<div class="report-card" style="color:#000!important;font-weight:600">{label[:58]}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💬 Ask", key=f"ask_{r}", use_container_width=True):
                st.session_state.focus_url = r
                st.rerun()
        with c2:
            st.markdown(
                f'<a href="{r}" target="_blank" style="text-decoration:none">'
                f'<button style="width:100%;padding:6px;border-radius:6px;border:1px solid #E5E5E5;'
                f'background:#fff;color:#3D3D3D;cursor:pointer;font-family:Inter,sans-serif;'
                f'font-size:0.78em;font-weight:500;letter-spacing:0.03em;text-transform:uppercase">'
                f'🔗 View</button></a>',
                unsafe_allow_html=True,
            )

# ── Header ────────────────────────────────────────────────────────────────────

hcol, bcol = st.columns([11, 1])
with hcol:
    st.markdown("""
        <h1 style="font-size:1.9em;font-weight:700;letter-spacing:-0.03em;color:#000;margin:0 0 4px">
            Fitch Voice Agent
        </h1>
        <p style="font-size:0.85em;color:#999;margin:0 0 20px;font-weight:400">
            Ask anything about Federico Canepa's published Fitch Ratings Structured Finance Reports
        </p>
    """, unsafe_allow_html=True)
with bcol:
    st.markdown("<div style='padding-top:12px'>", unsafe_allow_html=True)
    if st.button("ℹ️" if not st.session_state.show_banner else "✕", key="banner_toggle"):
        st.session_state.show_banner = not st.session_state.show_banner
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── Info banner ───────────────────────────────────────────────────────────────

if st.session_state.show_banner:
    st.markdown("""
<div class="info-banner" id="fitch-banner">
  <div style="font-size:0.7em;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#4056CE;margin-bottom:10px">
    About this app
  </div>
  <p style="font-size:0.88em;color:#3D3D3D;line-height:1.7;margin:0 0 12px">
    An AI-powered voice research assistant built on top of
    <a href="https://www.fitchratings.com/search/?query=federico+canepa" target="_blank"
       style="color:#4056CE;font-weight:500;text-decoration:none">Fitch Ratings Structured Finance Reports</a>
    authored by <strong>Federico Canepa</strong>. Answers are generated by Claude AI and spoken aloud
    in real time using the
    <a href="https://elevenlabs.io" target="_blank" style="color:#4056CE;font-weight:500;text-decoration:none">ElevenLabs TTS API</a>
    (<code style="background:#F5F5F5;padding:1px 5px;border-radius:4px;font-size:0.9em;color:#3D3D3D">eleven_turbo_v2</code>)
    via the official Python SDK, with voice selection and speed control via <code style="background:#F5F5F5;padding:1px 5px;border-radius:4px;font-size:0.9em;color:#3D3D3D">VoiceSettings</code>.
  </p>
  <div style="display:flex;gap:20px;flex-wrap:wrap;border-top:1px solid #E5E5E5;padding-top:10px;margin-top:4px">
    <span style="font-size:0.78em;color:#999;font-weight:500">① Select a report in the sidebar</span>
    <span style="font-size:0.78em;color:#999;font-weight:500">② Ask a question below</span>
    <span style="font-size:0.78em;color:#999;font-weight:500">③ Press ▶ to hear the answer</span>
  </div>
</div>

<script>
(function() {
    setTimeout(function() {
        var el = window.parent.document.getElementById('fitch-banner');
        if (el) {
            el.style.opacity = '0';
            el.style.maxHeight = '0';
            el.style.padding = '0 22px';
            el.style.marginBottom = '0';
            el.style.border = 'none';
        }
    }, 30000);
})();
</script>
""", unsafe_allow_html=True)

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("ANTHROPIC_API_KEY not set. Add it in Streamlit Cloud → Settings → Secrets.", icon="🔑")

# ── Focus indicator ───────────────────────────────────────────────────────────

if st.session_state.focus_url:
    focus_label = st.session_state.focus_url.rstrip("/").split("/")[-1].replace("-", " ").title()
    fc1, fc2 = st.columns([5, 1])
    with fc1:
        st.info(f"📄 Focused on: **{focus_label[:55]}**")
    with fc2:
        st.markdown("<div style='padding-top:8px'>", unsafe_allow_html=True)
        if st.button("✕ Clear", key="clear_focus"):
            st.session_state.focus_url = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

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
        with st.spinner("Thinking…"):
            try:
                from agent import answer
                response = answer(query, url_filter=active_focus)
            except Exception as e:
                response = f"Error: {e}"

        st.markdown(response)

        audio_bytes = None
        if voice_enabled:
            with st.spinner("Generating audio…"):
                audio_bytes, audio_source = generate_audio(response, selected_voice_id, speed)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
                st.markdown(
                    f'<div style="font-size:0.72em;color:#999;margin-top:2px">▶ Press play · via {audio_source}</div>',
                    unsafe_allow_html=True,
                )

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "audio": audio_bytes,
    })
