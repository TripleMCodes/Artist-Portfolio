# Aura Portfolio (VickyKae)

This is a Flask-based portfolio/hub site for an artist, including pages for Linktree-style links, releases, blogs, and more.

## 🧱 Project Structure (high level)

- `app.py` — Flask application factory, database setup, blueprint registration
- `templates/` — Jinja2 templates (includes `conditions.html`, `privacy.html`, etc.)
- `static/` — CSS/JS/assets (each blueprint may have its own `static/` folder)
- `models.py` — data models (SQLAlchemy)
- `seed.py` — initial seed data for development
- `blueprints/` (or similar) — route modules for pages (home, blog, contact, conditions, etc.)

## ✅ Requirements

- Python 3.10+
- (Optional) Postgres for production, or SQLite for local/dev

## ⚙️ Environment Variables

Recommended env vars (defaults are in `app.py`):

- `SECRET_KEY` – Flask secret key (default: `dev-secret-key-change-me`)
- `DATABASE_URL` – Postgres URL (`postgres://...` or `postgresql://...`)
- `SQLITE_PATH` – file path for SQLite (if not using `DATABASE_URL`)
- `LOGIN_VIEW_ENDPOINT` – login route endpoint (default: `admin.admin_login`)
- `LOG_LEVEL` – logging level (default: `INFO`)

## ▶️ Run Locally (development)

1. Create a venv and install deps:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   set FLASK_APP=app.py
   set FLASK_ENV=development
   python -m flask run
   ```

## 🗃️ Database

By default the app uses the `DATABASE_URL` env var. If not set, it will fall back to the hardcoded Postgres URI in `app.py` (you can change this) or to SQLite via `SQLITE_PATH`.

## 📌 Conditions Page

The terms/conditions page is rendered from:

- `templates/conditions.html`

You can update copy there as needed.

---