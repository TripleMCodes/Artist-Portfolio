from flask import render_template, request, redirect, url_for, flash, Blueprint
from models import Service, FAQ, User  # Corrected FAQ spelling
import logging

logging.basicConfig(level=logging.DEBUG)

service = Blueprint(
    'service',
    __name__,
    template_folder="html css js",
    static_folder="html css js",
    static_url_path="/service/static"
)

@service.route('/service')
def service_route():
    user = User.query.first()
    name = user.name.upper() if user else "ARTIST"

    services = Service.query.all()

    faq = FAQ.query.all()

    return render_template(
        'services.html', 
        services=services, 
        faq=faq, 
        name=name
    )