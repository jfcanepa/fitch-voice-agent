# Fitch Voice Agent

RAG-powered voice research assistant for Fitch Ratings structured finance reports.

## Architecture

```
Fitch URL
    │
    ▼
HTML Parser (r.jina.ai)
    │
    ▼
Text Chunks (400 tokens, 50 overlap)
    │
    ▼
Embeddings (ChromaDB local)
    │
    ▼
Vector Store (ChromaDB)
    │
    ▼
Query (top-6 retrieval)
    │
    ▼
Claude AI (claude-sonnet-4-6)
    │
    ▼
ElevenLabs TTS (eleven_turbo_v2)
    │
    ▼
Audio playback
```

## Features

- Ask natural-language questions about Fitch Ratings structured finance reports
- Real-time text-to-speech via ElevenLabs with adjustable speed, stability, and clarity
- Browser TTS fallback when ElevenLabs is unavailable
- Add custom report URLs for on-the-fly indexing
- Spanish mode for LATAM financial services demos (voice + Claude responses)
- Pre-loaded selection of Fitch structured finance reports
- Dark UI inspired by ElevenLabs design system

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd fitch-voice-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your API keys. Either create a `.env` file:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ELEVENLABS_API_KEY=sk_...
   ```
   Or for Streamlit Cloud, add them in **App settings → Secrets** (see `.streamlit/secrets.toml.example`).

4. Run locally:
   ```bash
   streamlit run app.py
   ```

## Secrets Required

| Key | Description |
|-----|-------------|
| `ANTHROPIC_API_KEY` | Claude API key for answer generation |
| `ELEVENLABS_API_KEY` | ElevenLabs API key for text-to-speech |
| `ELEVENLABS_VOICE_ID` | *(optional)* Default voice ID (defaults to Rachel) |
| `CHROMA_PERSIST_DIR` | *(optional)* ChromaDB storage path (defaults to `./chroma_db`) |

---

Built as a proof-of-concept for voice AI deployment in financial services. By Federico Canepa.
