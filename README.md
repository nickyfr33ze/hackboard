# Hackboard

A lightweight self-hosted dashboard for cybersecurity and developer news feeds, bookmarks, and Discord alerts. Accessible over Tailscale. No Docker required.

## Features

- Two-column dashboard: Security feeds left, Developer feeds right
- Auto-refreshes every 5 minutes in the browser
- High-severity items (zero-days, KEVs, CVSS >= 8.0) highlighted in red
- Discord webhook alerts — separate HIGH and GENERAL channels
- Bookmark manager
- Dynamic source management via UI (add, enable/disable, delete)
- Systemd service for always-on operation

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

```bash
cp .env.example .env  # or create .env manually
SECRET_KEY=dev .venv/bin/python3 run.py
```

Feeds are fetched immediately on startup and every 30 minutes thereafter. Hit **Refresh Feeds** on the dashboard to pull manually.

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

## Adding / Managing Sources

Go to `/sources` in the UI. Built-in defaults:

| Source | Category |
|---|---|
| CISA Alerts | Security |
| CISA KEV | Security |
| The Hacker News | Security |
| Bleeping Computer | Security |
| Krebs on Security | Security |
| Hacker News (HN) | Dev |
| Dev.to | Dev |
| GitHub Blog | Dev |

---

## Maintenance

| Task | How |
|---|---|
| Add a feed | Sources page in the UI |
| Adjust CVSS threshold | Edit env file, restart service |
| Add HIGH keywords | Edit `HIGH_KEYWORDS` in `app/feeds/classifier.py`, restart |
| Purge old items | `DELETE FROM feed_items WHERE fetched_at < datetime('now', '-30 days')` |
| View logs | `journalctl -u hackboard -f` |
