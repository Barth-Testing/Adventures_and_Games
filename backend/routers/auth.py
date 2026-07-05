from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Account
import hashlib
import os
import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = os.environ.get("JWT_SECRET", "supersecret-dev-key")
ALGORITHM = "HS256"

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str
    username: str

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    pwd = salt + password.encode()
    h = hashlib.sha256(pwd).hexdigest()
    return salt.hex() + ":" + h

def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, h = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        return hashlib.sha256(salt + password.encode()).hexdigest() == h
    except:
        return False

def create_token(username: str) -> str:
    payload = {"sub": username, "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Account).filter(Account.username == req.username).first()
    if existing:
        raise HTTPException(400, "Benutzername bereits vergeben")
    account = Account(username=req.username, password_hash=hash_password(req.password))
    db.add(account)
    db.commit()
    return {"message": "Registrierung erfolgreich"}

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.username == req.username).first()
    if not account or not verify_password(req.password, account.password_hash):
        raise HTTPException(401, "Ungültige Anmeldedaten")
    return TokenResponse(token=create_token(req.username), username=req.username)
