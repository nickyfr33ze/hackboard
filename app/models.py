import sqlite3
from contextlib import contextmanager
from email.utils import parsedate_to_datetime
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS feed_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guid TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('security', 'dev')),
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    summary TEXT,
    published_at TEXT,
    fetched_at TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'normal' CHECK(severity IN ('high', 'normal')),
    discord_sent INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    notes TEXT,
    tags TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    url TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('rss', 'kev_json')),
    category TEXT NOT NULL CHECK(category IN ('security', 'dev')),
    pdf_links INTEGER NOT NULL DEFAULT 0,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_feed_items_category ON feed_items(category);
CREATE INDEX IF NOT EXISTS idx_feed_items_fetched_at ON feed_items(fetched_at);
CREATE INDEX IF NOT EXISTS idx_feed_items_discord_sent ON feed_items(discord_sent);
"""

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db_path = app.config['DATABASE_PATH']
        import os
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.executescript(SCHEMA)
        conn.commit()
        _migrate_published_at(conn)
        conn.close()
    app.teardown_appcontext(close_db)

def _migrate_published_at(conn):
    """Normalize any existing published_at values that aren't ISO format."""
    rows = conn.execute(
        "SELECT id, published_at FROM feed_items WHERE published_at IS NOT NULL AND published_at NOT LIKE '____-__-__%'"
    ).fetchall()
    for row in rows:
        try:
            iso = parsedate_to_datetime(row[1]).isoformat()
            conn.execute("UPDATE feed_items SET published_at = ? WHERE id = ?", (iso, row[0]))
        except Exception:
            conn.execute("UPDATE feed_items SET published_at = NULL WHERE id = ?", (row[0],))
    if rows:
        conn.commit()
        print(f"[models] Migrated {len(rows)} published_at values to ISO format")

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur

def get_feed_items(category=None, limit=100, offset=0, search=None, date_from=None, date_to=None, sort='newest'):
    conditions = []
    args = []

    if category:
        conditions.append("category = ?")
        args.append(category)
    if search:
        conditions.append("(title LIKE ? OR summary LIKE ?)")
        args.extend([f"%{search}%", f"%{search}%"])
    if date_from:
        conditions.append("DATE(COALESCE(NULLIF(published_at,''), fetched_at)) >= ?")
        args.append(date_from)
    if date_to:
        conditions.append("DATE(COALESCE(NULLIF(published_at,''), fetched_at)) <= ?")
        args.append(date_to)

    direction = "ASC" if sort == 'oldest' else "DESC"
    order = f"COALESCE(NULLIF(published_at,''), fetched_at) {direction}"

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    args.extend([limit, offset])
    return query_db(
        f"SELECT * FROM feed_items {where} ORDER BY {order} LIMIT ? OFFSET ?",
        args
    )

def get_pending_discord_items():
    return query_db(
        "SELECT * FROM feed_items WHERE discord_sent = 0 AND category = 'security' ORDER BY fetched_at DESC"
    )

def mark_discord_sent(item_id):
    execute_db("UPDATE feed_items SET discord_sent = 1 WHERE id = ?", (item_id,))

def get_bookmarks():
    return query_db("SELECT * FROM bookmarks ORDER BY created_at DESC")

def add_bookmark(title, url, notes=None, tags=None):
    execute_db(
        "INSERT INTO bookmarks (title, url, notes, tags) VALUES (?, ?, ?, ?)",
        (title, url, notes, tags)
    )

def delete_bookmark(bookmark_id):
    execute_db("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))

def update_bookmark(bookmark_id, title, url, notes=None, tags=None):
    execute_db(
        "UPDATE bookmarks SET title = ?, url = ?, notes = ?, tags = ? WHERE id = ?",
        (title, url, notes, tags, bookmark_id)
    )

def get_sources(enabled_only=False):
    if enabled_only:
        return query_db("SELECT * FROM sources WHERE enabled = 1 ORDER BY category, name")
    return query_db("SELECT * FROM sources ORDER BY category, name")

def toggle_source(source_id):
    execute_db("UPDATE sources SET enabled = NOT enabled WHERE id = ?", (source_id,))

def delete_source(source_id):
    db = get_db()
    db.execute("DELETE FROM feed_items WHERE source = (SELECT name FROM sources WHERE id = ?)", (source_id,))
    db.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    db.commit()

def add_source(name, display_name, url, type_, category, pdf_links=False):
    execute_db(
        "INSERT INTO sources (name, display_name, url, type, category, pdf_links) VALUES (?, ?, ?, ?, ?, ?)",
        (name, display_name, url, type_, category, 1 if pdf_links else 0)
    )
