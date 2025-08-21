# iGaming Starter (FastAPI + PixiJS)

**Qué trae:**
- Backend FastAPI con RNG "provably fair" (server_seed hash publicado, client_seed, nonce).
- Endpoints `/health`, `/bets`, `/round`, `/history`, `/seeds/rotate`.
- Frontend HTML5 con PixiJS (crash MVP visual).

## Cómo correr
1) **Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```
Abrí `http://127.0.0.1:8000/docs` para probar.

2) **Frontend**
Abrí `frontend/index.html` en tu navegador. (Si tu navegador bloquea CORS, servilo con un servercito local, por ejemplo:
```bash
# en la carpeta frontend
python -m http.server 8080
# luego visitá http://127.0.0.1:8080
```

## Siguientes pasos
- Persistencia real en Postgres (ver `backend/schema.sql`).
- Autenticación (JWT), límites de apuesta y saldos reales.
- Simulador de RTP y telemetría.
- Skins y assets.
