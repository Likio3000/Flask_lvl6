# Filename: config.py
# ----- Start of file content -----
import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class DefaultConfig:
    """Default application configuration."""

    # --- Secret Key ---
    # IMPORTANT: Should be overridden with a strong random value in production!
    # Loaded from .env file or environment variable.
    # Fallback to 'dev' ONLY for local development if not set.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_unsafe_secret_key')
    if SECRET_KEY == 'dev_unsafe_secret_key':
        print("WARNING: Using default 'SECRET_KEY'. Set a strong SECRET_KEY environment variable for production.", file=os.sys.stderr)

    # --- Database ---
    # Default SQLite database path within the instance folder
    # Can be overridden by environment variable if needed (e.g., for different DB types)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('sqlite:///'):
         # Ensure the path is absolute if it's a relative SQLite URL
         db_name = DATABASE_URL.split('sqlite:///')[-1]
         DATABASE = os.path.join(basedir, 'instance', db_name) # Assuming relative path means relative to instance folder
    elif DATABASE_URL:
        DATABASE = DATABASE_URL # Use the full URL if provided (e.g., PostgreSQL) - requires additional drivers
    else:
        # Default to flaskr.sqlite in the instance folder
        DATABASE = os.path.join(basedir, 'instance', 'flaskr.sqlite')


    # --- Flask Environment ---
    # Set via FLASK_ENV environment variable (e.g., 'development', 'production')
    # Flask uses this to enable/disable debug mode, etc.
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production') # Default to production if not set
    DEBUG = FLASK_ENV == 'development'
    TESTING = FLASK_ENV == 'testing' # Or set explicitly for testing config

    # --- Application Specific Settings ---
    POSTS_PER_PAGE = os.environ.get('POSTS_PER_PAGE', 5) # Example app-specific setting


# Example of separate TestingConfig if needed
# class TestingConfig(DefaultConfig):
#     TESTING = True
#     SECRET_KEY = 'test_secret_key' # Use a fixed key for tests
#     DATABASE = os.path.join(basedir, 'instance', 'test_flaskr.sqlite')
#     POSTS_PER_PAGE = 3

# You could add DevelopmentConfig, ProductionConfig etc. if more complex setup is needed.

# ----- End of file content -----