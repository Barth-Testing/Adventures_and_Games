# Abenteuer & Games

D&D-inspired cooperative RPG mit Computer-Spielführer (GM). Erstellt für Kinder ab 6 Jahren und Erwachsene.

## Features

- Vollständig web-basiert (React + FastAPI)
- Computer-GM ersetzt den Spielleiter
- Freitexteingabe wird automatisch ausgewertet
- 4 Heldenklassen: Krieger, Magier, Schurke, Kleriker
- Rätsel und Kämpfe in einer epischen Geschichte
- Komplexitätsstufen (Einfach ab 6 Jahre bis Experte)

## Schnellstart

### Mit Docker

```bash
docker compose up -d
```

Danach unter `http://localhost:8080` erreichbar.

JWT_SECRET kann über Umgebungsvariable gesetzt werden:
```bash
JWT_SECRET=mein-geheimer-schlussel docker compose up -d
```

### Manuell (Entwicklung)

**Backend:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Dann `http://localhost:5173` öffnen (Frontend proxied `/api` an Backend).

## Projektstruktur

```
├── backend/
│   ├── game_engine/        # Spiel-Logik (Kampf, GM, Würfel, Bestiarium)
│   ├── routers/            # API-Endpunkte (Auth, Charaktere, Abenteuer, Kampf)
│   ├── main.py             # FastAPI Einstieg
│   ├── models.py           # SQLAlchemy Modelle
│   └── database.py         # DB-Konfiguration (SQLite)
├── frontend/
│   └── src/
│       ├── pages/          # Login, Dashboard, Charaktererstellung, Abenteuer
│       └── components/     # Layout
├── Dockerfile              # Multi-Stage Build
└── docker-compose.yml
```

## Erstes Abenteuer

"Der Schatten-Schatz der vergessenen Zitadelle" – Ein ca. 1,5-stündiges Abenteuer durch den Flüsterwald, alte Minen und eine verlassene Zitadelle. 3 Kämpfe, 2 Rätsel, mehrere NPCs.

## Lizenz

MIT
