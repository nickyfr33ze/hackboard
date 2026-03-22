from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from ..models import get_bookmarks, add_bookmark, delete_bookmark, update_bookmark

bp = Blueprint('bookmarks', __name__)

@bp.route('/')
def index():
    bookmarks = get_bookmarks()
    return render_template('bookmarks.html', bookmarks=bookmarks)

@bp.route('/add', methods=['POST'])
def add():
    title = request.form.get('title', '').strip()
    url = request.form.get('url', '').strip()
    notes = request.form.get('notes', '').strip() or None
    tags = request.form.get('tags', '').strip() or None
    if title and url:
        add_bookmark(title, url, notes, tags)
    return redirect(url_for('bookmarks.index'))

@bp.route('/<int:bookmark_id>/delete', methods=['POST'])
def delete(bookmark_id):
    delete_bookmark(bookmark_id)
    return redirect(url_for('bookmarks.index'))

@bp.route('/<int:bookmark_id>/edit', methods=['GET', 'POST'])
def edit(bookmark_id):
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        url = request.form.get('url', '').strip()
        notes = request.form.get('notes', '').strip() or None
        tags = request.form.get('tags', '').strip() or None
        if title and url:
            update_bookmark(bookmark_id, title, url, notes, tags)
        return redirect(url_for('bookmarks.index'))
    from ..models import query_db
    bookmark = query_db("SELECT * FROM bookmarks WHERE id = ?", (bookmark_id,), one=True)
    return render_template('bookmark_edit.html', bookmark=bookmark)
