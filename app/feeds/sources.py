import sqlite3
from flask import current_app

DEFAULT_SOURCES = [
    # ── General Security News ──────────────────────────────────────────────
    {
        "name": "cisa_alerts",
        "display_name": "CISA Alerts",
        "url": "https://www.cisa.gov/uscert/ncas/alerts.xml",
        "type": "rss",
        "category": "security",
        "pdf_links": True,
    },
    {
        "name": "cisa_kev",
        "display_name": "CISA KEV",
        "url": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        "type": "kev_json",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "thehackernews",
        "display_name": "The Hacker News",
        "url": "https://feeds.feedburner.com/TheHackersNews",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "bleepingcomputer",
        "display_name": "Bleeping Computer",
        "url": "https://www.bleepingcomputer.com/feed/",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "krebsonsecurity",
        "display_name": "Krebs on Security",
        "url": "https://krebsonsecurity.com/feed/",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },

    # ── Cyber Attacks / Incidents ──────────────────────────────────────────
    {
        "name": "cyberscoop",
        "display_name": "CyberScoop",
        "url": "https://cyberscoop.com/feed/",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "darkreading",
        "display_name": "Dark Reading",
        "url": "https://www.darkreading.com/rss/all",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },

    # ── Vulnerabilities ────────────────────────────────────────────────────
    {
        "name": "exploitdb",
        "display_name": "Exploit-DB",
        "url": "https://www.exploit-db.com/rss.xml",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "sans_isc",
        "display_name": "SANS ISC Diary",
        "url": "https://isc.sans.edu/rssfeed.xml",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },

    # ── Threat Intelligence ────────────────────────────────────────────────
    {
        "name": "talos",
        "display_name": "Talos Intelligence",
        "url": "https://blog.talosintelligence.com/feeds/posts/default",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "malwarebytes",
        "display_name": "Malwarebytes Labs",
        "url": "https://www.malwarebytes.com/blog/feed/index.xml",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "securelist",
        "display_name": "Securelist (Kaspersky)",
        "url": "https://securelist.com/feed/",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },

    # ── Developer ──────────────────────────────────────────────────────────
    {
        "name": "hackernews",
        "display_name": "Hacker News",
        "url": "https://hnrss.org/frontpage?points=100",
        "type": "rss",
        "category": "dev",
        "pdf_links": False,
    },
    {
        "name": "devto",
        "display_name": "Dev.to",
        "url": "https://dev.to/feed",
        "type": "rss",
        "category": "dev",
        "pdf_links": False,
    },
    {
        "name": "githublog",
        "display_name": "GitHub Blog",
        "url": "https://github.blog/feed/",
        "type": "rss",
        "category": "dev",
        "pdf_links": False,
    },

    # ── Reddit / Security ──────────────────────────────────────────────────
    {
        "name": "reddit_cybersecurity",
        "display_name": "r/cybersecurity",
        "url": "https://www.reddit.com/r/cybersecurity/.rss",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "reddit_sysadmin",
        "display_name": "r/sysadmin",
        "url": "https://www.reddit.com/r/sysadmin/.rss",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "reddit_hacking",
        "display_name": "r/hacking",
        "url": "https://www.reddit.com/r/hacking/.rss",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "reddit_networking",
        "display_name": "r/networking",
        "url": "https://www.reddit.com/r/networking/.rss",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "reddit_netsec",
        "display_name": "r/netsec",
        "url": "https://www.reddit.com/r/netsec/.rss",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "reddit_privacy",
        "display_name": "r/privacy",
        "url": "https://www.reddit.com/r/privacy/.rss",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "reddit_tails",
        "display_name": "r/tails",
        "url": "https://www.reddit.com/r/tails/.rss",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "reddit_thehatedone",
        "display_name": "r/thehatedone",
        "url": "https://www.reddit.com/r/thehatedone/.rss",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },
    {
        "name": "reddit_tor",
        "display_name": "r/TOR",
        "url": "https://www.reddit.com/r/TOR/.rss",
        "type": "rss",
        "category": "security",
        "pdf_links": False,
    },

    # ── Reddit / Dev ───────────────────────────────────────────────────────
    {
        "name": "reddit_linux",
        "display_name": "r/linux",
        "url": "https://www.reddit.com/r/linux/.rss",
        "type": "rss",
        "category": "dev",
        "pdf_links": False,
    },
    {
        "name": "reddit_homelab",
        "display_name": "r/homelab",
        "url": "https://www.reddit.com/r/homelab/.rss",
        "type": "rss",
        "category": "dev",
        "pdf_links": False,
    },
    {
        "name": "reddit_selfhosted",
        "display_name": "r/selfhosted",
        "url": "https://www.reddit.com/r/selfhosted/.rss",
        "type": "rss",
        "category": "dev",
        "pdf_links": False,
    },
    {
        "name": "reddit_theprimeagen",
        "display_name": "r/ThePrimeagen",
        "url": "https://www.reddit.com/r/ThePrimeagen/.rss",
        "type": "rss",
        "category": "dev",
        "pdf_links": False,
    },
]

def seed_sources(app):
    """Insert any DEFAULT_SOURCES entries not already present in the DB."""
    with app.app_context():
        conn = sqlite3.connect(app.config['DATABASE_PATH'])
        conn.row_factory = sqlite3.Row
        existing = {r['name'] for r in conn.execute("SELECT name FROM sources").fetchall()}
        added = 0
        for s in DEFAULT_SOURCES:
            if s['name'] not in existing:
                conn.execute(
                    "INSERT OR IGNORE INTO sources (name, display_name, url, type, category, pdf_links) VALUES (?, ?, ?, ?, ?, ?)",
                    (s['name'], s['display_name'], s['url'], s['type'], s['category'], 1 if s['pdf_links'] else 0)
                )
                added += 1
        if added:
            conn.commit()
            print(f"[sources] Seeded {added} new default source(s)")
        conn.close()

def get_enabled_sources(app):
    """Return enabled sources as list of dicts."""
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM sources WHERE enabled = 1 ORDER BY category, name").fetchall()
    conn.close()
    return [dict(r) for r in rows]
