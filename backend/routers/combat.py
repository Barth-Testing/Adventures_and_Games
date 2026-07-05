from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .adventure import active_sessions

router = APIRouter(prefix="/api/combat", tags=["combat"])

class CombatActionRequest(BaseModel):
    session_id: str
    character_name: str
    action: str
    target: str = ""

@router.post("/action")
def combat_action(req: CombatActionRequest):
    session = active_sessions.get(req.session_id)
    if not session:
        raise HTTPException(404, "Sitzung nicht gefunden")
    engine = session.gm.state.get("combat_engine")
    if not engine:
        raise HTTPException(400, "Kein aktiver Kampf")
    result = None
    if req.action in ("attack", "angreifen"):
        result = engine.player_attack(req.character_name, req.target) if req.target else engine.player_attack(req.character_name, None)
    elif req.action in ("defend", "verteidigen"):
        player = next((c for c in engine.combatants if c.is_player and c.name == req.character_name and c.is_alive), None)
        if player:
            player.ac += 2
            result = {"message": f"{player.name} verteidigt sich. RK +2"}
    elif req.action in ("wait", "warten"):
        result = {"message": f"{req.character_name} wartet."}
    elif req.action in ("flee", "fliehen"):
        from ..game_engine.dice import roll_d20
        roll = roll_d20()
        if roll > 12:
            session.gm.state["combat_active"] = False
            result = {"message": "Flucht erfolgreich!", "fled": True}
        else:
            result = {"message": "Flucht fehlgeschlagen!"}
    if not result:
        raise HTTPException(400, "Ungültige Aktion")
    next_turn = engine.next_turn()
    return {
        "combat_result": result,
        "next_turn": next_turn.name if next_turn else None,
        "combat_state": engine.get_state(),
        "combat_over": not engine.is_active,
        "engine": next_turn.is_player if next_turn else None
    }

@router.get("/state/{session_id}")
def combat_state(session_id: str):
    session = active_sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Sitzung nicht gefunden")
    engine = session.gm.state.get("combat_engine")
    if not engine:
        raise HTTPException(400, "Kein aktiver Kampf")
    return engine.get_state()
