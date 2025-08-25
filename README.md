# Gaming FastAPI

Separates a FastAPI backend and a Vite + React frontend.

## Environment variables

### Backend (Web Service)

- `DATABASE_URL`
- `JWT_SECRET`
- `ALLOWED_ORIGINS` comma separated list
- `DB_SCHEMA` optional schema name
- `GIT_SHA` optional commit hash injected by CI
- `SENTRY_DSN` optional

### Frontend (Static Site)

- `VITE_API_URL` = `https://gaming-fastapi.onrender.com`

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

Optional environment variable:

```
VITE_API_BASE_URL=http://localhost:8000
```

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
