from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

_scheduler = None

def init_scheduler(app):
    global _scheduler

    if _scheduler is not None:
        return

    from .feeds.fetcher import fetch_all_sources
    from .feeds.sources import seed_sources
    from .discord.webhook import send_pending_alerts

    # Seed default sources on first run
    seed_sources(app)

    interval = app.config.get('FEED_POLL_INTERVAL_MINUTES', 30)

    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(
        lambda: _run_cycle(app),
        trigger='interval',
        minutes=interval,
        next_run_time=datetime.now(),  # Run immediately on startup
        id='feed_cycle',
        replace_existing=True,
    )
    _scheduler.start()
    print(f"[scheduler] Started — polling every {interval} minutes")

def _run_cycle(app):
    from .feeds.fetcher import fetch_all_sources
    from .discord.webhook import send_pending_alerts
    with app.app_context():
        print("[scheduler] Running feed cycle...")
        fetch_all_sources(app)
        send_pending_alerts(app)
