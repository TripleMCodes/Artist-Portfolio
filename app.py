import logging
import os
from pathlib import Path
from typing import Optional

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, text
from sqlalchemy.engine import Engine

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Extensions
# ------------------------------------------------------------
db = SQLAlchemy()

# Guard to avoid registering the Engine connect listener multiple times
_SCHEMA_LISTENER_REGISTERED = False


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _normalize_database_url(url: Optional[str]) -> Optional[str]:
    """
    Render (and some providers) sometimes provide postgres:// URLs.
    SQLAlchemy expects postgresql://.
    """
    if not url:
        return None
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _build_sqlite_uri(sqlite_path: Optional[str]) -> str:
    """
    Builds a SQLite SQLAlchemy URI safely for both:
      - relative paths (sqlite:///portfolio.db)
      - absolute Linux paths (sqlite:////var/data/portfolio.db)

    Render disk paths are usually absolute, e.g. /var/data/portfolio.db
    """
    # If not provided, default to a local file in the working directory
    raw = (sqlite_path or "portfolio.db").strip()

    # Normalize slashes and expand ~
    p = Path(raw).expanduser()

    # Absolute path? Use 4 slashes (sqlite:////abs/path.db)
    if p.is_absolute():
        return f"sqlite:////{p.as_posix().lstrip('/')}"
    # Relative path? Use 3 slashes (sqlite:///rel/path.db)
    return f"sqlite:///{p.as_posix()}"


def _configure_schema_search_path(schema: str) -> None:
    """
    Force Postgres to use a specific schema via search_path.

    Set env var:
      DB_SCHEMA=aura

    This affects all connections created by SQLAlchemy in this process.
    """
    global _SCHEMA_LISTENER_REGISTERED

    schema = (schema or "").strip()
    if not schema:
        return

    # Prevent multiple registrations when create_app is called repeatedly
    if _SCHEMA_LISTENER_REGISTERED:
        return

    @event.listens_for(Engine, "connect")
    def _set_search_path(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        # NOTE: schema name is trusted from env. Keep it simple: lowercase + underscores recommended.
        cursor.execute(f"SET search_path TO {schema}")
        cursor.close()

    _SCHEMA_LISTENER_REGISTERED = True


def _ensure_schema_exists(app: Flask, schema: str) -> None:
    """
    Fail fast if DB_SCHEMA is set but the schema doesn't exist.

    Important: We only enforce this when using Postgres.
    """
    schema = (schema or "").strip()
    if not schema:
        return

    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not uri.startswith("postgresql://"):
        logger.warning(
            "DB_SCHEMA is set (%s) but database is not Postgres. Ignoring schema check.",
            schema,
        )
        return

    with app.app_context():
        try:
            exists = db.session.execute(
                text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :s LIMIT 1"),
                {"s": schema},
            ).scalar()
        except Exception as e:
            raise RuntimeError(
                f"Could not verify schema '{schema}'. "
                f"Check DATABASE_URL connectivity and permissions. Original error: {e}"
            ) from e

        if not exists:
            raise RuntimeError(
                f"DB_SCHEMA='{schema}' is set but the schema does not exist in the database.\n"
                f"Create it first (example): CREATE SCHEMA {schema};\n"
                f"Then ensure the DB user has USAGE/CREATE privileges on that schema."
            )


def _configure_database(app: Flask) -> None:
    """
    Configure SQLALCHEMY_DATABASE_URI for Render + local dev.

    Priority:
      1) DATABASE_URL (Postgres on Render)
      2) SQLITE_PATH (SQLite on Render w/ disk, or local custom path)
      3) local sqlite file: portfolio.db
    """
    database_url = _normalize_database_url(os.getenv("DATABASE_URL"))
    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        return

    sqlite_uri = _build_sqlite_uri(os.getenv("SQLITE_PATH"))
    app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_uri


def _init_auth(app: Flask) -> None:
    login_manager = LoginManager()
    login_manager.login_view = os.getenv("LOGIN_VIEW_ENDPOINT", "admin.admin_login")
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        from models import User  # local import to avoid circular deps
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None


def _register_blueprints(app: Flask) -> None:
    # Local imports keep startup predictable and avoid import-time side effects.
    from home.route import home
    from terms.route import terms
    from blog_post.route import blog
    from blog.route import all_blogs
    from contact.route import contct
    from privacy.route import privacy
    from services.route import service
    from linktree.route import linktree
    from events.route import events
    from media.route import media
    from gallery.route import gallery
    from about.route import about
    from conditions.route import conditions
    from admin_login.route import admin

    blueprints = [
        home,
        blog,
        terms,
        contct,
        privacy,
        service,
        all_blogs,
        linktree,
        events,
        media,
        gallery,
        about,
        conditions,
        admin,
    ]

    for bp in blueprints:
        app.register_blueprint(bp)


# ------------------------------------------------------------
# App Factory
# ------------------------------------------------------------
def create_app() -> Flask:
    app = Flask(__name__)

    # Core config (Render-safe)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    _configure_database(app)

    # Optional schema isolation (Postgres)
    schema = os.getenv("DB_SCHEMA")
    if schema:
        _configure_schema_search_path(schema)

    # Init extensions
    db.init_app(app)
    Migrate(app, db)

    if schema:
        _ensure_schema_exists(app, schema)

    # Auth
    _init_auth(app)

    # Health endpoint (Render-friendly)
    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}, 200

    # Blueprints
    _register_blueprints(app)

    return app
