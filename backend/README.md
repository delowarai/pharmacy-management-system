# Pharmacy API (FastAPI + PostgreSQL)

## PyCharm development setup

1. Open this folder in PyCharm.
2. Create a Python 3.12 virtual environment.
3. Run `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`, then configure the variables in PyCharm Run Configuration (or load them with an env-file plugin).
5. Create PostgreSQL database/user or run only the database: `docker compose up -d db`.
6. Run `uvicorn app.main:app --reload --port 8000`.
7. Open `http://localhost:8000/docs`. First login: `admin` / `Admin@123`.

For a quick SQLite demo, omit `DATABASE_URL`; `pharmacy.db` is created automatically.

## Production

Run `docker compose up -d --build`. Before doing so, replace the database password and `JWT_SECRET` in `docker-compose.yml`, restrict `CORS_ORIGINS` to the real frontend URL, put the API behind HTTPS (Nginx/Caddy), and change the initial admin password. Back up the named PostgreSQL volume daily with `pg_dump`.

The API docs list every implemented endpoint. Stock deductions are transactional and FEFO; expired batches are not sold.

