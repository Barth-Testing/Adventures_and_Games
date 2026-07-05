from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import init_db, engine
from .models import Base
from .routers import auth, characters, adventure, combat

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Abenteuer &amp; Games - RPG Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/api/health")
def health():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(characters.router)
app.include_router(adventure.router)
app.include_router(combat.router)
