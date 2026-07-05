from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from ..game_engine.tts import generate_audio, get_audio_path, _text_hash
import asyncio

router = APIRouter(prefix="/api/tts", tags=["tts"])

AUDIO_DIR = Path(__file__).parent.parent.parent / "data" / "audio"

@router.get("/generate")
async def generate(text: str):
    if not text.strip():
        raise HTTPException(400, "Kein Text angegeben")
    fname = await generate_audio(text)
    if not fname:
        raise HTTPException(500, "TTS-Fehler")
    fpath = get_audio_path(fname)
    if fpath.exists():
        return FileResponse(str(fpath), media_type="audio/mpeg")
    raise HTTPException(500, "Audio nicht gefunden")

@router.get("/{text_hash}.mp3")
async def serve_audio(text_hash: str):
    fpath = AUDIO_DIR / f"{text_hash}.mp3"
    if fpath.exists():
        return FileResponse(str(fpath), media_type="audio/mpeg")
    raise HTTPException(404, "Audio nicht gefunden")
