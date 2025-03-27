# Filename: ./flaskr/errors.py
# ----- Start of file content -----
from flask import Blueprint, render_template, current_app

# Create blueprint for error handlers
bp = Blueprint('errors', __name__)

@bp.app_errorhandler(403)
def forbidden_error(error):
    """Custom handler for 403 Forbidden errors."""
    current_app.logger.warning(f"Forbidden access attempt: {error}")
    return render_template('errors/403.html'), 403

@bp.app_errorhandler(404)
def not_found_error(error):
    """Custom handler for 404 Not Found errors."""
    current_app.logger.warning(f"Resource not found: {error}")
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    """Custom handler for 500 Internal Server errors."""
    # In a real app, you might want to rollback the database session here
    # from .db import get_db
    # db = get_db()
    # db.session.rollback() # Example if using SQLAlchemy
    current_app.logger.error(f"Internal server error: {error}", exc_info=True)
    return render_template('errors/500.html'), 500

# You can add handlers for other common errors like 400, 401, etc.
# ----- End of file content -----