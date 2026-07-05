from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Character
from ..game_engine.gm_system import GMSystem

router = APIRouter(prefix="/api/adventure", tags=["adventure"])
active_sessions = {}

class StartAdventureRequest(BaseModel):
    username: str
    character_id: int

class ActionRequest(BaseModel):
    session_id: str
    action_text: str

class AdventureSession:
    def __init__(self, gm: GMSystem, character):
        self.gm = gm
        self.character = character
        self.session_id = f"{character.name}_{id(self)}"

def _build_response(session, result):
    state = session.gm.get_state()
    nd = state.get("node_data") or {}
    return {
        "session_id": session.session_id,
        "narrative": result.get("narrative", nd.get("narrative", "")),
        "audio_text": result.get("audio_text", nd.get("audio_text", "")),
        "options": result.get("options", nd.get("options", [])),
        "scene": nd.get("scene", ""),
        "combat_active": state.get("combat_active", False),
        "combat_state": state.get("combat_state"),
        "puzzle": result.get("puzzle", nd.get("puzzle")),
        "puzzle_active": result.get("puzzle_active", bool(nd.get("puzzle"))),
        "puzzle_solved": result.get("puzzle_solved"),
        "puzzle_failed": result.get("puzzle_failed"),
        "adventure_complete": nd.get("adventure_complete", False),
        "combat_start": result.get("combat_start", nd.get("type") == "combat"),
        "loot": result.get("loot", nd.get("loot", [])),
        "roll": result.get("roll"),
        "success": result.get("success"),
        "combat_result": result.get("combat_result"),
        "combat_over": result.get("combat_over"),
        "your_turn": result.get("your_turn"),
    }

@router.post("/start")
def start_adventure(req: StartAdventureRequest, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == req.character_id).first()
    if not character:
        raise HTTPException(404, "Charakter nicht gefunden")
    gm = GMSystem([character])
    session = AdventureSession(gm, character)
    active_sessions[session.session_id] = session
    result = gm.process_action(character, "start")
    return _build_response(session, result)

@router.post("/action")
def process_action(req: ActionRequest):
    session = active_sessions.get(req.session_id)
    if not session:
        raise HTTPException(404, "Sitzung nicht gefunden")
    result = session.gm.process_action(session.character, req.action_text)
    return _build_response(session, result)

@router.get("/state/{session_id}")
def get_state(session_id: str):
    session = active_sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Sitzung nicht gefunden")
    state = session.gm.get_state()
    nd = state.get("node_data") or {}
    return {
        "session_id": session_id,
        "narrative": nd.get("narrative", ""),
        "audio_text": nd.get("audio_text", ""),
        "options": nd.get("options", []),
        "scene": nd.get("scene", ""),
        "combat_active": state.get("combat_active", False),
        "combat_state": state.get("combat_state"),
        "puzzle": nd.get("puzzle"),
        "adventure_complete": nd.get("adventure_complete", False)
    }
