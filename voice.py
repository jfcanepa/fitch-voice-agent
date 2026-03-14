"""
voice.py — Speak text using the ElevenLabs TTS API.

Streams audio directly to the system's default audio output so there is no
latency from writing a file first.
"""

import os
import subprocess
import tempfile

from dotenv import load_dotenv
from elevenlabs import ElevenLabs

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel
MODEL_ID = "eleven_turbo_v2"  # low-latency model

_client: ElevenLabs | None = None


def _get_client() -> ElevenLabs:
    global _client
    if _client is None:
        if not ELEVENLABS_API_KEY:
            raise RuntimeError("ELEVENLABS_API_KEY is not set in .env")
        _client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    return _client


def speak(text: str) -> None:
    """Convert text to speech and play it immediately."""
    if not text.strip():
        return

    client = _get_client()

    audio_bytes = b"".join(
        client.text_to_speech.convert(
            voice_id=VOICE_ID,
            text=text,
            model_id=MODEL_ID,
            output_format="mp3_44100_128",
        )
    )

    _play_audio(audio_bytes)


def _play_audio(audio_bytes: bytes) -> None:
    """Write mp3 to a temp file and play with afplay (macOS) or ffplay."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    # macOS
    if _cmd_exists("afplay"):
        subprocess.run(["afplay", tmp_path], check=True)
    # Linux / fallback
    elif _cmd_exists("ffplay"):
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", tmp_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        raise RuntimeError("No audio player found. Install ffplay or run on macOS.")

    os.unlink(tmp_path)


def _cmd_exists(cmd: str) -> bool:
    import shutil
    return shutil.which(cmd) is not None
