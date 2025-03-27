# Filename: ./flaskr/db.py
# ----- Start of file content -----
import sqlite3
from datetime import datetime
from typing import Any, Optional

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db() -> sqlite3.Connection:
    """
    Get a database connection for the current application context.

    If a connection doesn't exist in the 'g' object, it creates a new one,
    configures it with a Row factory, and stores it in 'g'.

    Returns:
        The SQLite database connection.
    """
    if 'db' not in g:
        try:
            db_path = current_app.config['DATABASE']
            g.db = sqlite3.connect(
                db_path,
                detect_types=sqlite3.PARSE_DECLTYPES  # Enable type detection
            )
            # Return rows as dictionary-like objects
            g.db.row_factory = sqlite3.Row
            current_app.logger.debug(f"Database connection opened for {db_path}")
        except KeyError:
             current_app.logger.critical("DATABASE configuration key not found!")
             raise RuntimeError("DATABASE configuration is missing.")
        except sqlite3.Error as e:
             current_app.logger.error(f"Database connection failed: {e}")
             raise # Re-raise the exception after logging
    return g.db


def close_db(e: Optional[Exception] = None) -> None:
    """
    Close the database connection if it exists in the 'g' object.

    This function is registered to be called automatically when the
    application context is torn down.

    Args:
        e: An optional exception that might have occurred during request handling.
    """
    db = g.pop('db', None)

    if db is not None:
        try:
            db.close()
            current_app.logger.debug("Database connection closed.")
        except sqlite3.Error as e:
            current_app.logger.error(f"Error closing database: {e}")
    if e:
        current_app.logger.error(f"Application context teardown due to exception: {e}")


def init_db() -> None:
    """
    Initialize the database by executing the schema script.

    Reads the schema.sql file and executes its SQL commands using the
    current database connection.
    """
    db = get_db()
    schema_path = 'schema.sql' # Relative to the flaskr package directory

    try:
        # Use open_resource which looks relative to the package path
        with current_app.open_resource(schema_path) as f:
            # Read the file content and decode it from bytes to string
            sql_script = f.read().decode('utf8')
            # Execute the entire script
            db.executescript(sql_script)
        current_app.logger.info("Database schema initialized successfully.")
    except FileNotFoundError:
        current_app.logger.error(f"Schema file not found at expected location: {schema_path}")
    except sqlite3.Error as e:
        current_app.logger.error(f"Error executing schema script: {e}")
        # Optionally, you might want to rollback or handle the partial execution
        db.rollback() # Rollback in case of error during executescript


@click.command('init-db', help='Clear existing data and create new tables.')
@with_appcontext # Ensures Flask app context is available
def init_db_command() -> None:
    """
    Flask CLI command to initialize the database.
    Usage: flask init-db
    """
    try:
        init_db()
        click.echo('Initialized the database.')
    except Exception as e:
        # Catch potential errors during init_db and report them
        click.echo(f'Error initializing database: {e}', err=True)
        current_app.logger.critical(f'Failed to initialize database via CLI: {e}')


# Register custom type converters/adapters if needed
# Example: Ensure Python datetime objects are stored in ISO format
# sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
# sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode('utf-8')))
# Note: The default CURRENT_TIMESTAMP stores as text, which PARSE_DECLTYPES might handle. Check if needed.


def init_app(app: Any) -> None:
    """
    Register database functions with the Flask application instance.

    - Registers the teardown function to close the DB connection after each request.
    - Adds the 'init-db' command to the Flask CLI.

    Args:
        app: The Flask application instance.
    """
    # Tell Flask to call close_db when cleaning up after returning the response
    app.teardown_appcontext(close_db)

    # Add the init_db_command to the Flask CLI group
    app.cli.add_command(init_db_command)
    app.logger.debug("Database functions registered with the application.")

# ----- End of file content -----