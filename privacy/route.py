from flask import render_template, Blueprint
import logging
logging.basicConfig(level=logging.DEBUG)
from models import User, Admin

privacy = Blueprint(
    'privacy',
    __name__,
    template_folder='html css js',
    static_folder='html css js',
    static_url_path='/privacy/static'
)

@privacy.route('/privacy')
def privacy_route():
    user = User.query.first()
    name = user.name.upper() if user else "ARTIST"

    admin = Admin.query.first()
    email = admin.email if admin else "contact@example.com"

    return render_template('privacy.html', name=name, email=email)