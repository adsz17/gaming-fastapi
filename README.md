# Gaming FastAPI

Separates a FastAPI backend and a Vite + React frontend.

## Environment variables

| Service  | Variables |
|----------|-----------|
| Backend  | `DATABASE_URL`, `JWT_SECRET`, `ALLOWED_ORIGINS`, `DB_SCHEMA`?, `SENTRY_DSN`? |
| Frontend | `VITE_API_URL`, `VITE_WS_URL`? |

`ALLOWED_ORIGINS` accepts a JSON list (`["https://front.com","http://localhost:5173"]`) or a comma-separated string (`https://front.com,http://localhost:5173`).

See the `.env.example` files in each folder.

## Run locally

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn api.main:app --reload
```

### Frontend

```bash
npm i
npm run dev
```

The frontend runs on [http://localhost:5173](http://localhost:5173) and uses `VITE_API_URL` for API calls.

### Admin Panel

The admin interface lives under `/admin` and authenticates using a token stored in `localStorage` (`adminToken`) which is sent via the `X-Admin-Token` header.

Generate the UI components with [shadcn/ui](https://ui.shadcn.com):

```
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input badge table tabs dialog dropdown-menu
```

### Schema search_path

If the default `public` schema is not writable, set `DB_SCHEMA` and the
application will issue `SET search_path TO <schema>, public` for all
connections. Alembic respects the same variable.

## Deploy on Render

1. Commit all changes including `render.yaml`.
2. Create a new Blueprint in Render pointing to this repository.
3. The blueprint provisions a Static Site and a Python Web Service.
4. Static Site:
   - **Build**: `npm ci && npm run build`
   - **Publish**: `frontend/dist`
   - Optional SPA rewrite: `/*` → `/index.html`
5. Web Service:
   - **Start**: `uvicorn api.main:app --host 0.0.0.0 --port 10000`
6. Set the environment variables shown above for each service.

The backend exposes `GET /health` returning `{ "ok": true }`.
