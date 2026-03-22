from flask import Blueprint, render_template, request, redirect, url_for
from ..models import get_sources, toggle_source, delete_source, add_source, toggle_reddit_sources, query_db

bp = Blueprint('sources', __name__)

@bp.route('/')
def index():
    sources = get_sources()
    result = query_db("SELECT COUNT(*) FROM sources WHERE name LIKE 'reddit_%' AND enabled = 1", one=True)
    reddit_any_enabled = result[0] > 0
    return render_template('sources.html', sources=sources, reddit_any_enabled=reddit_any_enabled)

@bp.route('/add', methods=['POST'])
def add():
    name = request.form.get('name', '').strip().lower().replace(' ', '_')
    display_name = request.form.get('display_name', '').strip()
    url = request.form.get('url', '').strip()
    type_ = request.form.get('type', 'rss')
    category = request.form.get('category', 'security')
    pdf_links = bool(request.form.get('pdf_links'))
    if name and display_name and url:
        try:
            add_source(name, display_name, url, type_, category, pdf_links)
        except Exception:
            pass  # Duplicate name — silently ignore
    next_url = request.form.get('next') or url_for('sources.index')
    return redirect(next_url)

@bp.route('/toggle-reddit', methods=['POST'])
def toggle_reddit():
    toggle_reddit_sources()
    return redirect(url_for('sources.index'))

@bp.route('/<int:source_id>/toggle', methods=['POST'])
def toggle(source_id):
    toggle_source(source_id)
    return redirect(url_for('sources.index'))

@bp.route('/<int:source_id>/delete', methods=['POST'])
def delete(source_id):
    delete_source(source_id)
    return redirect(url_for('sources.index'))
