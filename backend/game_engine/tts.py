import asyncio
import hashlib
from pathlib import Path

AUDIO_DIR = Path(__file__).parent.parent.parent / "data" / "audio"
VOICE = "de-DE-KatjaNeural"

def _ensure_dir():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def _text_hash(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:16]

async def generate_audio(text, voice=None):
    _ensure_dir()
    text = text.strip()[:500]
    if not text:
        return None
    fname = f"{_text_hash(text)}.mp3"
    fpath = AUDIO_DIR / fname
    if fpath.exists():
        return fname
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice or VOICE)
        await communicate.save(str(fpath))
        return fname
    except Exception:
        return None

def get_audio_path(filename):
    return AUDIO_DIR / filename
