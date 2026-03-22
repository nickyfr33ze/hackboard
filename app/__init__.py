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

    # Init scheduler (guard against Flask debug mode double-process)
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        init_scheduler(app)

    return app
