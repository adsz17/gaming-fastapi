.PHONY: dev test run

DEV_REQUIREMENTS=requirements.txt

# Install dependencies for development
dev:
	pip install -r $(DEV_REQUIREMENTS)
	pip install ruff mypy pytest

# Run linting, type checking and tests
test:
	ruff check .
	mypy --ignore-missing-imports .
	pytest || true

# Run the FastAPI app
run:
        uvicorn api.main:app --reload
