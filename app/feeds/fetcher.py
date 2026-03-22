import feedparser
import requests
import sqlite3
from datetime import datetime, timezone, timedelta
from flask import current_app
import time

from .classifier import classify_severity
from .sources import get_enabled_sources

def _db_conn(app):
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

def _insert_item(conn, guid, source, category, title, url, summary, published_at, severity):
    conn.execute(
        """INSERT OR IGNORE INTO feed_items
           (guid, source, category, title, url, summary, published_at, fetched_at, severity)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (guid, source, category, title, url, summary, published_at,
         datetime.now(timezone.utc).isoformat(), severity)
    )

def fetch_rss(source, app):
    url = source['url']
    name = source['name']
    category = source['category']
    max_items = app.config.get('MAX_ITEMS_PER_SOURCE', 50)
    threshold = app.config.get('CVSS_HIGH_THRESHOLD', 8.0)

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"[fetcher] Error fetching {name}: {e}")
        return 0

    conn = _db_conn(app)
    count = 0
    for entry in feed.entries[:max_items]:
        guid = getattr(entry, 'id', None) or entry.get('link', '')
        if not guid:
            continue
        title = entry.get('title', '(no title)')
        link = entry.get('link', '')
        summary = entry.get('summary', '') or entry.get('description', '')
        published = entry.get('published', '') or entry.get('updated', '')
        severity = classify_severity(title, summary, name, threshold)
        _insert_item(conn, guid, name, category, title, link, summary, published, severity)
        count += 1

    conn.commit()
    conn.close()
    print(f"[fetcher] {name}: processed {count} items")
    return count

def fetch_kev(source, app):
    url = source['url']
    name = source['name']
    max_items = app.config.get('MAX_ITEMS_PER_SOURCE', 50)

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[fetcher] Error fetching KEV: {e}")
        return 0

    vulnerabilities = data.get('vulnerabilities', [])[:max_items]
    conn = _db_conn(app)
    count = 0
    for vuln in vulnerabilities:
        cve_id = vuln.get('cveID', '')
        if not cve_id:
            continue
        guid = f"cisa_kev:{cve_id}"
        title = f"{cve_id} — {vuln.get('vulnerabilityName', '')}"
        url_link = f"https://www.cisa.gov/known-exploited-vulnerabilities-catalog"
        summary = (
            f"Vendor: {vuln.get('vendorProject', '')} | "
            f"Product: {vuln.get('product', '')} | "
            f"Due: {vuln.get('dueDate', '')} | "
            f"{vuln.get('shortDescription', '')}"
        )
        published = vuln.get('dateAdded', '')
        _insert_item(conn, guid, name, 'security', title, url_link, summary, published, 'high')
        count += 1

    conn.commit()
    conn.close()
    print(f"[fetcher] cisa_kev: processed {count} items")
    return count

def fetch_all_sources(app):
    sources = get_enabled_sources(app)
    total = 0
    for source in sources:
        if source['type'] == 'rss':
            total += fetch_rss(source, app)
        elif source['type'] == 'kev_json':
            total += fetch_kev(source, app)
    print(f"[fetcher] fetch_all_sources complete: {total} items processed")
    return total
