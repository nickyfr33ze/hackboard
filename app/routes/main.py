from flask import Blueprint, render_template, current_app
from ..models import get_feed_items

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    security_items = get_feed_items(category='security', limit=50)
    dev_items = get_feed_items(category='dev', limit=50)
    return render_template('index.html', security_items=security_items, dev_items=dev_items)
