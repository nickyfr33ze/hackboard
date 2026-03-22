# Hackboard

A lightweight self-hosted dashboard for cybersecurity and developer news feeds, bookmarks, and Discord alerts. Accessible over Tailscale. No Docker required.

## Features

- Two-column dashboard: Security feeds left, Developer feeds right
- Auto-refreshes every 5 minutes in the browser (manual Refresh button also available)
- Search feeds by keyword, filter by date range, sort newest/oldest
- High-severity items (zero-days, KEVs, CVSS >= 8.0) highlighted in red with badge
- Discord webhook alerts — separate HIGH and GENERAL channels with rate limiting
- Manual article submission — paste a URL, title is auto-fetched from the page
- Quick-add feed panel on the dashboard toolbar
- Bookmark manager (add, edit, delete, tags, notes)
- Dynamic source management UI (add, enable/disable, delete — survives restarts)
- APScheduler background polling every 30 minutes, immediate fetch on startup
- Systemd service for always-on operation

---

## Default Feed Sources

### Security — General News
| Source | Feed |
|---|---|
| CISA Alerts | RSS (PDF links enabled) |
| CISA KEV | JSON (Known Exploited Vulnerabilities) |
| The Hacker News | RSS |
| Bleeping Computer | RSS |
| Krebs on Security | RSS |

### Security — Cyber Attacks & Incidents
| Source | Feed |
|---|---|
| CyberScoop | RSS |
| Dark Reading | RSS |

### Security — Vulnerabilities
| Source | Feed |
|---|---|
| Exploit-DB | RSS |
| SANS ISC Diary | RSS |

### Security — Threat Intelligence
| Source | Feed |
|---|---|
| Talos Intelligence | RSS |
| Malwarebytes Labs | RSS |
| Securelist (Kaspersky) | RSS |

### Developer
| Source | Feed |
|---|---|
| Hacker News (top posts) | RSS |
| Dev.to | RSS |
| GitHub Blog | RSS |

---

## Quick Start (Linux)

### 1. Clone and set up the venv

```bash
git clone <repo-url> ~/dev/git/hackboard
cd ~/dev/git/hackboard
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. Create the environment file

```bash
sudo mkdir -p /etc/hackboard
sudo nano /etc/hackboard/hackboard.env
```

Paste and fill in:

```env
SECRET_KEY=change-me-to-something-random
DATABASE_PATH=/var/lib/hackboard/hackboard.db

# Optional — Discord webhook URLs for alerts
DISCORD_HIGH_WEBHOOK=
DISCORD_GENERAL_WEBHOOK=

# Optional — tuning (defaults shown)
FEED_POLL_INTERVAL_MINUTES=30
CVSS_HIGH_THRESHOLD=8.0
MAX_ITEMS_PER_SOURCE=50
```

```bash
sudo chmod 600 /etc/hackboard/hackboard.env
```

### 3. Create the data directory

```bash
sudo mkdir -p /var/lib/hackboard
sudo chown $USER:$USER /var/lib/hackboard
```

### 4. Install and start the systemd service

Edit `hackboard.service` first — update `User`, `Group`, `WorkingDirectory`, and `ExecStart` to match your username and paths if they differ from `nick`.

```bash
sudo cp hackboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now hackboard
```

Check it's running:

```bash
systemctl status hackboard
journalctl -u hackboard -f
```

The dashboard is now available at `http://<your-ip>:5000`.

### 5. Tailscale access

If Tailscale is installed, the dashboard is reachable at `http://<tailscale-ip>:5000` from any device on your tailnet. No additional config needed — Flask binds to `0.0.0.0`.

If port 5000 is blocked by a local firewall:

```bash
sudo ufw allow in on tailscale0 to any port 5000
```

---

## Development (local/macOS)

> **Note:** Port 5000 is used by AirPlay Receiver on macOS. Use 5001 or disable AirPlay Receiver in System Settings.

```bash
cp .env.example .env  # fill in SECRET_KEY at minimum
SECRET_KEY=dev .venv/bin/python3 -c "
from app import create_app
app = create_app()
app.run(host='0.0.0.0', port=5001, debug=True)
"
```

`debug=True` enables hot-reload for templates and static files without restarts.

---

## Configuration

All config is via environment variables (`.env` for dev, `/etc/hackboard/hackboard.env` for prod).

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(required)* | Flask session secret |
| `DATABASE_PATH` | `hackboard.db` | Path to SQLite DB |
| `DISCORD_HIGH_WEBHOOK` | *(empty)* | Webhook for zero-days, KEVs, CVSS >= threshold |
| `DISCORD_GENERAL_WEBHOOK` | *(empty)* | Webhook for all other security items |
| `FEED_POLL_INTERVAL_MINUTES` | `30` | How often to poll feeds |
| `CVSS_HIGH_THRESHOLD` | `8.0` | CVSS score that triggers HIGH severity |
| `MAX_ITEMS_PER_SOURCE` | `50` | Max items ingested per source per poll |

---

## Managing Sources

Sources are managed at `/sources` in the UI or via the **Add Feed** button on the dashboard toolbar. Changes survive restarts — new default sources are automatically added on next startup without affecting user-added or modified sources.

---

## Maintenance

| Task | How |
|---|---|
| Add a feed | Dashboard toolbar → Add Feed, or Sources page |
| Add a one-off article | Dashboard toolbar → Add Article |
| Adjust CVSS threshold | Edit env file, restart service |
| Add HIGH alert keywords | Edit `HIGH_KEYWORDS` in `app/feeds/classifier.py`, restart |
| Purge old items | `DELETE FROM feed_items WHERE fetched_at < datetime('now', '-30 days')` |
| View logs | `journalctl -u hackboard -f` |
| Update after git pull | `pip install -r requirements.txt && sudo systemctl restart hackboard` |
