import os
import sys
from fastapi.testclient import TestClient

# ensure backend path and env
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
os.environ["DATABASE_URL"] = "postgresql+psycopg://user:pass@localhost/test"
os.environ["RATE_LIMIT_PER_MIN"] = "1000"
os.environ["JWT_SECRET"] = "change-me-please"

import api.main as main  # noqa: E402

client = TestClient(main.app)


def test_preflight_register():
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
    }
    res = client.options("/api/auth/register", headers=headers)
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert res.headers.get("access-control-allow-credentials") == "true"
