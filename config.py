import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "hackboard.db")
    DISCORD_HIGH_WEBHOOK = os.environ.get("DISCORD_HIGH_WEBHOOK", "")
    DISCORD_GENERAL_WEBHOOK = os.environ.get("DISCORD_GENERAL_WEBHOOK", "")
    FEED_POLL_INTERVAL_MINUTES = int(os.environ.get("FEED_POLL_INTERVAL_MINUTES", 30))
    CVSS_HIGH_THRESHOLD = float(os.environ.get("CVSS_HIGH_THRESHOLD", 8.0))
    MAX_ITEMS_PER_SOURCE = int(os.environ.get("MAX_ITEMS_PER_SOURCE", 50))
