# Filename: ./flaskr/auth.py
# ----- Start of file content -----
import functools
from typing import Any, Callable, Optional, Union

from flask import (Blueprint, current_app, flash, g, redirect,
                   render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.wrappers import Response

from flaskr.db import get_db

# Create blueprint for authentication routes, prefixed with /auth
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register() -> Union[str, Response]:
    """
    Handle user registration.
    GET: Displays the registration form.
    POST: Processes form submission, validates input, creates new user.
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '') # Don't strip password initially
        db = get_db()
        error: Optional[str] = None

        # Basic input validation
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        # Add password complexity check if desired here
        # elif len(password) < 8:
        #     error = 'Password must be at least 8 characters long.'

        if error is None:
            # Attempt to insert the new user into the database
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)), # Hash password before storing
                )
                db.commit()
                current_app.logger.info(f"User '{username}' registered successfully.")
            except db.IntegrityError:
                # This error occurs if the username already exists (due to UNIQUE constraint)
                error = f"Username '{username}' is already taken."
                current_app.logger.warning(f"Registration failed: {error}")
            except db.Error as e:
                # Catch other potential database errors
                db.rollback() # Rollback transaction on error
                error = "An internal error occurred during registration. Please try again later."
                current_app.logger.error(f"Database error during registration for '{username}': {e}")
            else:
                # Registration successful, redirect to login page
                flash(f"User '{username}' successfully registered. Please log in.", 'success')
                return redirect(url_for("auth.login"))

        # If there was an error, flash the message
        flash(error, 'error') # Specify category for styling

    # For GET requests or if POST had an error, render the registration template
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login() -> Union[str, Response]:
    """
    Handle user login.
    GET: Displays the login form.
    POST: Processes form submission, validates credentials, starts session.
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        error: Optional[str] = None
        user: Optional[Any] = None # Use Any or create a User dataclass/dict type

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else:
            # Fetch the user from the database
            try:
                user = db.execute(
                    'SELECT * FROM user WHERE username = ?', (username,)
                ).fetchone()
            except db.Error as e:
                 error = "An internal error occurred during login. Please try again later."
                 current_app.logger.error(f"Database error during login attempt for '{username}': {e}")

            if user is None:
                error = 'Incorrect username or password.' # Generic error for security
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect username or password.' # Generic error

        if error is None and user is not None:
            # Credentials are valid, store user id in session
            session.clear() # Clear any previous session data
            session['user_id'] = user['id']
            current_app.logger.info(f"User '{username}' (ID: {user['id']}) logged in successfully.")
            # Redirect to the main index page after login
            flash(f"Welcome back, {username}!", 'success')
            return redirect(url_for('index'))

        # If there was an error, flash the message
        flash(error, 'error')
        current_app.logger.warning(f"Login failed for username '{username}': {error}")

    # For GET requests or if POST had an error, render the login template
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user() -> None:
    """
    Load user data into g.user before each request if a user_id is in the session.
    Runs automatically before any view function within the application context.
    """
    user_id: Optional[int] = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        try:
            # Fetch user data from DB based on session user_id
            g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()
            # If user ID in session doesn't match a user (e.g., user deleted), clear session
            if g.user is None:
                session.clear()
                current_app.logger.warning(f"User ID {user_id} from session not found in database. Session cleared.")
        except Exception as e:
            # Handle potential DB errors during user loading
            g.user = None
            current_app.logger.error(f"Error loading user {user_id} from session: {e}")

@bp.route('/logout')
def logout() -> Response:
    """
    Log the user out by clearing the session.
    """
    username = g.user['username'] if g.user else 'Unknown user'
    session.clear() # Remove user_id and any other data from the session
    current_app.logger.info(f"User '{username}' logged out.")
    flash("You have been logged out.", 'info')
    return redirect(url_for('index')) # Redirect to the main index page


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to protect views that require a logged-in user.

    Redirects unauthenticated users to the login page.

    Args:
        view: The view function to decorate.

    Returns:
        The decorated view function.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs: Any) -> Any:
        if g.user is None:
            # User is not logged in, redirect to login page
            current_app.logger.debug(f"Unauthorized access attempt to '{request.path}'. Redirecting to login.")
            flash("You need to be logged in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url)) # Optional: add next param
        # User is logged in, proceed with the original view function
        return view(**kwargs)

    return wrapped_view
