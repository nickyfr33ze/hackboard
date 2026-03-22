from flask import Blueprint, render_template, request
from ..models import get_feed_items

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    search = request.args.get('search', '').strip() or None
    date_from = request.args.get('date_from', '').strip() or None
    date_to = request.args.get('date_to', '').strip() or None
    sort = request.args.get('sort', 'newest')
    if sort not in ('newest', 'oldest'):
        sort = 'newest'

    filters = dict(search=search, date_from=date_from, date_to=date_to, sort=sort, limit=50)
    security_items = get_feed_items(category='security', **filters)
    dev_items = get_feed_items(category='dev', **filters)

    return render_template('index.html',
        security_items=security_items,
        dev_items=dev_items,
        search=search or '',
        date_from=date_from or '',
        date_to=date_to or '',
        sort=sort,
    )
