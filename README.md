# Gaming FastAPI

Separates a FastAPI backend and a Vite + React frontend.

## Environment variables

### Backend (`backend/.env`)

- `ENV` - environment name, default `production`.
- `JWT_SECRET` - secret key for JWT tokens.
- `DATABASE_URL` - database connection string.
- `CORS_ORIGINS` - JSON array with allowed origins.

See `backend/.env.example`.

### Frontend (`frontend/.env`)

- `VITE_API_URL` - base URL for the backend API (optional, defaults to same origin).

See `frontend/.env.example`.

## Run locally

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

### Frontend

```bash
npm ci
npm run dev
```

The frontend will be served on [http://localhost:5173](http://localhost:5173) and proxy API requests to the backend.

## Deploy on Render

1. Commit all changes including `render.yaml`.
2. Create a new Blueprint in Render pointing to this repository.
3. The blueprint provisions a Static Site and a Python Web Service.
4. Add the following Redirects/Rewrites to the Static Site:
   - `/api/*` → `https://gaming-fastapi.onrender.com/api/:splat` (Rewrite)
   - `/*` → `/index.html` (Rewrite)
5. Set environment variables as shown above for each service.

The backend service runs:

```
uvicorn api.main:app --host 0.0.0.0 --port 10000
```

The static site publishes `frontend/dist` after running `npm ci && npm run build`.

## Quick QA

### Development

1. Run the backend on port `8000`.
2. In another terminal, run `npm run dev`.
3. Use the register form to send a `POST` request to `/api/auth/register`.

### Production (Render)

The frontend on `https://gaming-fastapi-1.onrender.com` should issue requests to
`https://gaming-fastapi.onrender.com` via the `/api/*` rewrite.
