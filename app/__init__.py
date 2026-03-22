from flask import Flask
from .models import init_db
from .scheduler import init_scheduler
import os

def create_app(config=None):
    app = Flask(__name__, template_folder='templates', static_folder='../static')

    # Load config
    app.config.from_object('config.Config')
    if config:
        app.config.update(config)

    # Init DB
    init_db(app)

    # Register blueprints
    from .routes.main import bp as main_bp
    from .routes.bookmarks import bp as bookmarks_bp
    from .routes.sources import bp as sources_bp
    from .routes.api import bp as api_bp
    from .routes.blog import bp as blog_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(bookmarks_bp, url_prefix='/bookmarks')
    app.register_blueprint(sources_bp, url_prefix='/sources')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(blog_bp, url_prefix='/blog')

    # Source badge map: source name → (label, hex background color)
    app.jinja_env.globals['SOURCE_BADGES'] = {
        'cisa_alerts':      ('CISA',  '#27ae60'),
        'cisa_kev':         ('KEV',   '#e74c3c'),
        'thehackernews':    ('THN',   '#c0392b'),
        'bleepingcomputer': ('BC',    '#2471a3'),
        'krebsonsecurity':  ('KOS',   '#7d3c98'),
        'cyberscoop':       ('CS',    '#148f77'),
        'darkreading':      ('DR',    '#ba4a00'),
        'exploitdb':        ('EDB',   '#922b21'),
        'sans_isc':         ('SANS',  '#1a252f'),
        'talos':            ('TALOS', '#1f618d'),
        'malwarebytes':     ('MWB',   '#1e8449'),
        'securelist':       ('KSP',   '#6e2f1a'),
        'hackernews':       ('HN',    '#ff6600'),
        'devto':            ('DEV',   '#3c3c3c'),
        'githublog':        ('GH',    '#24292e'),
        'manual':           ('USER',  '#626567'),
    }

    # Init scheduler (guard against Flask debug mode double-process)
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        init_scheduler(app)

    return app
