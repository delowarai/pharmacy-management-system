# Pharmacy API (FastAPI + PostgreSQL)

## PyCharm development setup

1. Open this folder in PyCharm.
2. Create a Python 3.12 virtual environment.
3. Run `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`, then configure the variables in PyCharm Run Configuration (or load them with an env-file plugin).
5. Create PostgreSQL database/user or run only the database: `docker compose up -d db`.
6. Run `uvicorn app.main:app --reload --port 8000`.
7. Open `http://localhost:8000/docs`. The initial username/password come from `INITIAL_ADMIN_USERNAME` and `INITIAL_ADMIN_PASSWORD` in `.env`.

For a quick SQLite demo, omit `DATABASE_URL`; `pharmacy.db` is created automatically.

## Production

Run `docker compose up -d --build`. Before doing so, replace the database password, `JWT_SECRET`, and initial administrator password in `docker-compose.yml`, restrict `CORS_ORIGINS` to the real frontend URL, and put the API behind HTTPS (Nginx/Caddy). Back up the named PostgreSQL volume daily with `pg_dump`.

The API docs list every implemented endpoint. Stock deductions are transactional and FEFO; expired batches are not sold.

