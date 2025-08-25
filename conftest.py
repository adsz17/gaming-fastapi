import os
import sys
from pathlib import Path

# Ensure the backend package is on the Python path so tests can import `api`
backend_path = Path(__file__).resolve().parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

os.environ.setdefault("ALLOWED_ORIGINS", '["http://localhost:5173"]')
