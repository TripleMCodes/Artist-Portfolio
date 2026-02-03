from flask import Flask, render_template, request, Response, url_for, redirect, g
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import logging
from models import Admin, Artist 
import os

logging.basicConfig(level=logging.DEBUG)

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.secret_key = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-change-me"
    )

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://",
                "postgresql://",
                1
            )
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        # Local fallback C:\Users\nkosikhona\Aura portfolio\app.py
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:/Users/nkosikhona/Aura portfolio/portfolio.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # --- Auth ---
    

    login_manager = LoginManager()
    login_manager.login_view = "admin.login"
    login_manager.init_app(app)

    


    @app.before_request
    def resolve_artist():
        # Only resolve artist when route actually has artist_slug
        if not request.view_args:
            g.artist = None
            g.artist_id = None
            return

        artist_slug = request.view_args.get('artist_slug')
        if not artist_slug:
            g.artist = None
            g.artist_id = None
            return

        artist = Artist.query.filter_by(slug=artist_slug).first_or_404()
        g.artist = artist
        g.artist_id = artist.id



    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

   
    @app.context_processor
    def inject_artist_vars():
        """Makes 'artist' available to all HTML templates automatically."""
        return dict(artist=g.artist)

    
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

    app.register_blueprint(home)
    app.register_blueprint(blog)
    app.register_blueprint(terms)
    app.register_blueprint(contct)
    app.register_blueprint(privacy)
    app.register_blueprint(service)
    app.register_blueprint(all_blogs)
    app.register_blueprint(linktree)
    app.register_blueprint(events)
    app.register_blueprint(media)
    app.register_blueprint(gallery)
    app.register_blueprint(about)
    app.register_blueprint(conditions)
    app.register_blueprint(admin)

    @app.route('/')
    def root():
        return redirect(url_for('home.index', artist_slug='Aura'))

    migrate = Migrate(app, db)

    return app
