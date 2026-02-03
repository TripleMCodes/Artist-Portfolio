from flask import render_template, Blueprint, abort
from models import User, Admin
import logging

logging.basicConfig(level=logging.DEBUG)

conditions = Blueprint(
    'conditions',
    __name__,
    template_folder='html css js',
    static_folder='html css js',
    static_url_path='/conditions/static'
)

@conditions.route('/conditions')
def conditions_route():
    user = User.query.first()

    admin = Admin.query.first()
    name = user.name.upper()
    email = admin.email if admin else ""

    return render_template(
        'conditions.html',
        name=name,
        email=email
    )
