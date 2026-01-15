# ADMS API

Advanced Drone Management System - Backend API

## Development

```bash
# Install dependencies
uv sync --all-groups

# Run development server
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .

# Run type checker
uv run pyright
```

## Stack

- FastAPI
- SQLAlchemy 2.0
- PostgreSQL 18
- Redis 8
- Python 3.14
