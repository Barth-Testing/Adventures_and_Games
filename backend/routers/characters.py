from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import Account, Character

router = APIRouter(prefix="/api/characters", tags=["characters"])

class CharacterCreate(BaseModel):
    username: str
    name: str
    class_name: str
    race: str = "Mensch"
    level: int = 1

class CharacterResponse(BaseModel):
    id: int
    name: str
    char_class: str
    race: str
    level: int
    hp_current: int
    hp_max: int
    ac: int
    attack_bonus: int
    damage_bonus: int
    initiative_bonus: int
    spell_save_dc: int

def get_account(username: str, db: Session) -> Account:
    account = db.query(Account).filter(Account.username == username).first()
    if not account:
        raise HTTPException(404, "Account nicht gefunden")
    return account

@router.post("/create")
def create_character(req: CharacterCreate, db: Session = Depends(get_db)):
    account = get_account(req.username, db)
    character = Character(account_id=account.id, name=req.name, char_class=req.class_name, race=req.race, level=req.level)
    db.add(character)
    db.commit()
    db.refresh(character)
    return {"message": f"Charakter {req.name} erstellt", "id": character.id}

@router.get("/all")
def list_all_characters(db: Session = Depends(get_db)):
    chars = db.query(Character).all()
    return [
        CharacterResponse(
            id=c.id, name=c.name, char_class=c.char_class, race=c.race,
            level=c.level, hp_current=c.hp_current, hp_max=c.hp_max,
            ac=c.ac, attack_bonus=c.attack_bonus, damage_bonus=c.damage_bonus,
            initiative_bonus=c.initiative_bonus, spell_save_dc=c.spell_save_dc
        ) for c in chars
    ]

@router.get("/list/{username}")
def list_characters(username: str, db: Session = Depends(get_db)):
    account = get_account(username, db)
    chars = db.query(Character).filter(Character.account_id == account.id).all()
    return [
        CharacterResponse(
            id=c.id, name=c.name, char_class=c.char_class, race=c.race,
            level=c.level, hp_current=c.hp_current, hp_max=c.hp_max,
            ac=c.ac, attack_bonus=c.attack_bonus, damage_bonus=c.damage_bonus,
            initiative_bonus=c.initiative_bonus, spell_save_dc=c.spell_save_dc
        ) for c in chars
    ]

@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(character_id: int, db: Session = Depends(get_db)):
    c = db.query(Character).filter(Character.id == character_id).first()
    if not c:
        raise HTTPException(404, "Charakter nicht gefunden")
    return CharacterResponse(
        id=c.id, name=c.name, char_class=c.char_class, race=c.race,
        level=c.level, hp_current=c.hp_current, hp_max=c.hp_max,
        ac=c.ac, attack_bonus=c.attack_bonus, damage_bonus=c.damage_bonus,
        initiative_bonus=c.initiative_bonus, spell_save_dc=c.spell_save_dc
    )
