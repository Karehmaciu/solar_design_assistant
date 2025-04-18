import os
from gunicorn.app.base import BaseApplication
from app import create_app

class StandaloneApplication(BaseApplication):
    """Gunicorn application for WSGI server deployment"""
    
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == "__main__":
    # Get configuration from environment variables
    port = int(os.environ.get("PORT", 8003))
    workers = int(os.environ.get("WORKERS", 4))
    threads = int(os.environ.get("THREADS", 2))
    
    # Create Flask app
    flask_app = create_app("production")
    
    # Configure Gunicorn
    options = {
        "bind": f"0.0.0.0:{port}",
        "workers": workers,
        "threads": threads,
        "worker_class": "gthread",
        "timeout": 120,
        "accesslog": "-",  # log to stdout
        "errorlog": "-",   # log to stderr
    }
    
    # Run the app with Gunicorn
    print(f"Starting server on port {port} with {workers} workers")
    StandaloneApplication(flask_app, options).run()