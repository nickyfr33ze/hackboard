import requests
import time
import sqlite3
from datetime import datetime, timezone, timedelta
from flask import current_app

def send_webhook(url, content):
    """Send a message to a Discord webhook URL."""
    if not url:
        return False
    try:
        resp = requests.post(url, json={"content": content}, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"[discord] Webhook error: {e}")
        return False

def send_pending_alerts(app):
    """Send unsent security feed items to Discord. Skips items older than 24h on first run."""
    high_webhook = app.config.get('DISCORD_HIGH_WEBHOOK', '')
    general_webhook = app.config.get('DISCORD_GENERAL_WEBHOOK', '')
    reddit_webhook = app.config.get('DISCORD_REDDIT_WEBHOOK', '')

    if not high_webhook and not general_webhook and not reddit_webhook:
        return

    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    items = conn.execute(
        "SELECT * FROM feed_items WHERE discord_sent = 0 AND category = 'security' ORDER BY fetched_at ASC"
    ).fetchall()

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    sent_count = 0

    for item in items:
        # Skip items older than 24h (first-run spam guard)
        try:
            fetched = datetime.fromisoformat(item['fetched_at'].replace('Z', '+00:00'))
            if fetched.tzinfo is None:
                fetched = fetched.replace(tzinfo=timezone.utc)
            if fetched < cutoff:
                # Mark as sent so we don't check again
                conn.execute("UPDATE feed_items SET discord_sent = 1 WHERE id = ?", (item['id'],))
                continue
        except Exception:
            pass

        severity = item['severity']
        title = item['title']
        url = item['url']
        source = item['source']

        content = f"**[{source.upper()}]** {title}\n{url}"

        if source.startswith('reddit_'):
            webhook_url = reddit_webhook
        elif severity == 'high':
            webhook_url = high_webhook
        else:
            webhook_url = general_webhook

        if webhook_url:
            success = send_webhook(webhook_url, content)
            if success:
                conn.execute("UPDATE feed_items SET discord_sent = 1 WHERE id = ?", (item['id'],))
                sent_count += 1
                time.sleep(2)  # Rate limit guard: 2s between sends
        else:
            # No webhook configured for this severity — mark as sent to avoid retrying
            conn.execute("UPDATE feed_items SET discord_sent = 1 WHERE id = ?", (item['id'],))

    conn.commit()
    conn.close()
    print(f"[discord] Sent {sent_count} alerts")
