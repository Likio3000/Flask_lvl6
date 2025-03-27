# Filename: ./flaskr/__init__.py
# ----- Start of file content -----
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Any, Mapping, Optional
import datetime # <--- IMPORT DATETIME

from flask import Flask, render_template
from markdown import markdown


def create_app(test_config: Optional[Mapping[str, Any]] = None) -> Flask:
    """
    Application factory function to create and configure the Flask application.

    Args:
        test_config: Configuration mapping for testing. Defaults to None.

    Returns:
        The configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)

    # --- 1. Load Configuration ---
    # ... (config loading code remains the same) ...
    app.config.from_object('config.DefaultConfig')

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
        app.config.from_prefixed_env()
    else:
        app.config.from_mapping(test_config)


    # --- 2. Ensure Instance Folder Exists ---
    # ... (instance folder code remains the same) ...
    try:
        os.makedirs(app.instance_path)
        app.logger.info(f"Instance path created at {app.instance_path}")
    except OSError:
        pass

    # --- 3. Configure Logging ---
    # ... (logging code remains the same) ...
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/flaskr.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Flaskr startup')
    else:
        app.logger.setLevel(logging.DEBUG)

    # --- 4. Initialize Extensions & Database ---
    from . import db
    db.init_app(app)

    # --- 5. Register Blueprints ---
    from . import auth, blog, errors
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(errors.bp) # Register error handlers blueprint

    app.add_url_rule('/', endpoint='index')

    # --- 6. Register Custom Jinja Filters ---
    @app.template_filter('markdown')
    def markdown_filter(s: str) -> str:
        """Converts Markdown text to HTML."""
        return markdown(s, extensions=['fenced_code', 'tables'])

    # --- Inject 'now' into Jinja context --- # <--- ADD THIS SECTION ---
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.utcnow()}
    # -------------------------------------- #

    # --- 7. Define a simple test route (optional) ---
    @app.route('/hello')
    def hello() -> str:
        app.logger.debug("Accessed /hello route")
        return 'Hello, World!'

    app.logger.info("Flask application created successfully.")
    return app

# ----- End of file content -----