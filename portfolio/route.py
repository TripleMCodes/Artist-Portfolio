from flask import render_template, request, redirect, url_for, Blueprint
import logging
logging.basicConfig(level=logging.DEBUG)

portfolio = Blueprint(
    'portfolio',
    __name__,
    template_folder="html css js",
    static_folder="html css js",
    static_url_path='/portfolio/static'
)

@portfolio.route('/portfolio')
def my_portfolio():
    return render_template('portfolio.html')
