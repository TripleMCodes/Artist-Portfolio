from flask import Flask, render_template, request, Response, url_for, redirect
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from pathlib import Path
from flask_login import LoginManager
import os
logging.basicConfig(level=logging.DEBUG)

db_uri =  os.getenv("DATABASE_URL")

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    if db_uri and db_uri.startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] =  db_uri
    else:
        app.secret_key = "akjdkjfi[qjkkadhfapifjakdkoen"
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///portfolio.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from models import Admin
    login_manager = LoginManager()
    login_manager.login_view = "admin.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return redirect(url_for('home.index'))
    

    from home.route import home
    from terms.route import terms
    from blog_post.route import blog
    from blog.route import all_blogs
    from contact.route import contct
    from privacy.route import privacy
    from services.route import service
    # from portfolio.route import portfolio
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
    # app.register_blueprint(portfolio)
    app.register_blueprint(linktree)
    app.register_blueprint(events)
    app.register_blueprint(media)
    app.register_blueprint(gallery)
    app.register_blueprint(about)
    app.register_blueprint(conditions)
    #admin related
    app.register_blueprint(admin)

    migrate = Migrate(app, db)

    return app