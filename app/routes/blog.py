from flask import Blueprint, request, redirect, url_for, flash
from html.parser import HTMLParser
import requests as http
from datetime import datetime, timezone

from ..models import execute_db
from ..feeds.classifier import classify_severity
from flask import current_app

bp = Blueprint('blog', __name__)

class _TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_title = False
        self.title = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data

def fetch_page_title(url):
    try:
        resp = http.get(url, timeout=8, headers={'User-Agent': 'Hackboard/1.0'})
        resp.raise_for_status()
        parser = _TitleParser()
        parser.feed(resp.text[:8192])  # Only parse the head section
        return parser.title.strip() or None
    except Exception:
        return None

@bp.route('/add', methods=['POST'])
def add():
    url = request.form.get('url', '').strip()
    title = request.form.get('title', '').strip()
    source_name = request.form.get('source_name', '').strip() or 'manual'
    category = request.form.get('category', 'security')
    summary = request.form.get('summary', '').strip() or None

    if not url:
        return redirect(url_for('main.index'))

    if not title:
        title = fetch_page_title(url) or url

    threshold = current_app.config.get('CVSS_HIGH_THRESHOLD', 8.0)
    severity = classify_severity(title, summary or '', source_name, threshold)
    now = datetime.now(timezone.utc).isoformat()
    guid = f"manual:{url}"

    execute_db(
        """INSERT OR IGNORE INTO feed_items
           (guid, source, category, title, url, summary, published_at, fetched_at, severity)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (guid, source_name, category, title, url, summary, now, now, severity)
    )

    return redirect(url_for('main.index'))

@bp.route('/<int:item_id>/delete', methods=['POST'])
def delete(item_id):
    execute_db("DELETE FROM feed_items WHERE id = ? AND source NOT IN (SELECT name FROM sources)", (item_id,))
    return redirect(url_for('main.index'))
