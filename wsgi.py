# Filename: wsgi.py
# ----- Start of file content -----
# Entry point for WSGI servers like Gunicorn or uWSGI
# Example usage: gunicorn "wsgi:app"

from flaskr import create_app
import os

# Create the Flask app instance using the factory
# Detect FLASK_ENV for configuration loading within create_app
app = create_app()

if __name__ == "__main__":
    # Run the development server if script is executed directly
    # Get host and port from environment variables or use defaults
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    # Debug mode is controlled by FLASK_ENV inside create_app
    app.run(host=host, port=port)

# ----- End of file content -----