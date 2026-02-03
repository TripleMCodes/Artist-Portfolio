from flask import render_template, Blueprint
import logging
from models import User, ProfileImg

logging.basicConfig(level=logging.DEBUG)

linktree = Blueprint(
    "linktree",
    __name__,
    template_folder='html css js',
    static_folder='html css js',
    static_url_path='/linktree/static'
)

@linktree.route('/linktree')
def linktree_route():
    from models import LinktreeLink, LinktreeConfig
    profile_pic = ProfileImg.query.first()
    user = User.query.first()
    name = user.name.upper()
    links = LinktreeLink.query.order_by(LinktreeLink.order).all()
    config = LinktreeConfig.query.first()
    
    # If no config exists, create default
    if not config:
        from app import db
        config = LinktreeConfig()
        db.session.add(config)
        db.session.commit()
    
    return render_template('linktree.html', links=links, config=config, name=name, profile_pic=profile_pic.profile_picture)