from flask import Blueprint, jsonify, current_app
from ..feeds.fetcher import fetch_all_sources
from ..discord.webhook import send_pending_alerts

bp = Blueprint('api', __name__)

@bp.route('/feeds/refresh', methods=['POST', 'GET'])
def refresh_feeds():
    app = current_app._get_current_object()
    count = fetch_all_sources(app)
    send_pending_alerts(app)
    return jsonify({"status": "ok", "items_processed": count})

@bp.route('/health')
def health():
    return jsonify({"status": "ok"})
