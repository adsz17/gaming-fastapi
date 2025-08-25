import json
import os
from typing import List, Optional


def parse_allowed_origins(raw: Optional[str]) -> List[str]:
    """Parse a JSON list or comma-separated string of origins."""
    if not raw:
        return []
    raw = raw.strip()
    try:
        if raw.startswith("["):
            data = json.loads(raw)
            if isinstance(data, list):
                return [str(o).strip() for o in data if str(o).strip()]
            return []
        return [o.strip() for o in raw.split(",") if o.strip()]
    except Exception:
        return [raw] if raw else []


DATABASE_URL = os.environ["DATABASE_URL"]
JWT_SECRET = os.environ["JWT_SECRET"]
ALLOWED_ORIGINS = parse_allowed_origins(os.getenv("ALLOWED_ORIGINS"))
DB_SCHEMA = os.getenv("DB_SCHEMA")
SENTRY_DSN = os.getenv("SENTRY_DSN")
