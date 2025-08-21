from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))

def test_postgres_url_uses_psycopg(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    if "api.db" in sys.modules:
        del sys.modules["api.db"]
    import api.db as db  # noqa: E402
    assert db.engine.url.drivername == "postgresql+psycopg"
    # Clean up so other tests can configure their own database URL
    del sys.modules["api.db"]
