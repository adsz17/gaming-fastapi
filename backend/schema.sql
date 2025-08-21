-- Minimal Postgres schema (optional; replace in-memory)
CREATE TABLE IF NOT EXISTS rounds (
  id SERIAL PRIMARY KEY,
  user_id UUID NOT NULL,
  game_code TEXT NOT NULL DEFAULT 'crash_v1',
  bet NUMERIC(18,6) NOT NULL CHECK (bet > 0),
  payout NUMERIC(18,6) NOT NULL DEFAULT 0,
  server_seed_hash TEXT NOT NULL,
  client_seed TEXT NOT NULL,
  nonce BIGINT NOT NULL,
  result_json JSONB NOT NULL,
  idem TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, idem)
);

CREATE INDEX IF NOT EXISTS idx_rounds_user ON rounds(user_id);
CREATE INDEX IF NOT EXISTS idx_rounds_created ON rounds(created_at);
