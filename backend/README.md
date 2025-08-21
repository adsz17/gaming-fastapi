# iGaming Starter - Backend (FastAPI)

Endpoints (dev):
- `GET /health`
- `POST /bets` `{ user_id, bet, client_seed }`
- `POST /round` `{ user_id, bet, client_seed }` -> returns result + server_seed_hash + nonce
- `GET /history?limit=20&user_id=<id>`
- `POST /seeds/rotate` (rotate server seed; illustrative)

## Run locally
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Then open `http://127.0.0.1:8000/docs` for Swagger UI.

Example usage:

```bash
# register and obtain JWT
curl -sX POST localhost:8000/auth/register -d '{"email":"a@a.com","password":"pw"}' -H 'Content-Type: application/json'

# deposit into wallet
curl -sX POST localhost:8000/wallet/txn \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{"amount":10,"reason":"dep","idempotency_key":"abc"}'

# play crash round
curl -sX POST localhost:8000/crash/round \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{"bet":5,"client_seed":"seed","idem":"r1"}'

# metrics
curl localhost:8000/metrics
```

## Database migrations

Database schema changes are managed with Alembic. Set the `DATABASE_URL`
environment variable and run:

```bash
alembic upgrade head
```

This will create or upgrade the tables in the configured database.

## Tests

Run linters, type checking and tests from the project root:

```bash
ruff check
mypy --ignore-missing-imports backend
pytest -q
```
