# URL Shortener Backend

Production-style URL shortening service built with FastAPI, SQLAlchemy, PostgreSQL/SQLite, Redis-ready caching, validation, analytics, rate limiting, Docker and tests.

## Features
- Create short URLs with optional custom aliases and expiry
- Fast redirects with click analytics
- PostgreSQL-ready persistence via SQLAlchemy
- Optional Redis caching
- In-memory rate limiting for local development
- REST API with automatic Swagger/OpenAPI docs
- Health checks
- Unit tests
- Docker Compose setup

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

The default local database is SQLite. Set DATABASE_URL to PostgreSQL for production.

## Docker

```bash
docker compose up --build
```

## API
- POST /api/v1/urls
- GET /{short_code}
- GET /api/v1/urls/{short_code}
- DELETE /api/v1/urls/{short_code}
- GET /health
- GET /api/v1/stats

## Example

```bash
curl -X POST http://127.0.0.1:8000/api/v1/urls \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://example.com/very/long/path","custom_alias":"demo"}'
```

Then visit http://127.0.0.1:8000/demo.

## Architecture

Client -> FastAPI -> validation/service layer -> SQLAlchemy -> PostgreSQL
                                  \-> Redis cache (optional)
                                  \-> rate limiter

The service keeps the API layer thin and isolates persistence/business logic so the system can be extended without rewriting routes.
