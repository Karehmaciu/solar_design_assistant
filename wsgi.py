import os
import platform
from app import create_app

# Create and expose Flask app for Gunicorn/Render to use
flask_app = create_app("production")

if __name__ == "__main__":
    # For local development
    port = int(os.environ.get("PORT", 8003))
    
    if platform.system() == "Windows":
        # On Windows, use Flask's built-in server for development
        print(f"Starting Flask development server on port {port}")
        flask_app.run(host="0.0.0.0", port=port, debug=False)
    else:
        # On Unix systems, use Gunicorn (only import if available)
        try:
            from gunicorn.app.base import BaseApplication
            
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

            # Configure Gunicorn
            workers = int(os.environ.get("WORKERS", 4))
            threads = int(os.environ.get("THREADS", 2))
            
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
            print(f"Starting Gunicorn server on port {port} with {workers} workers")
            StandaloneApplication(flask_app, options).run()
        except ImportError:
            print("Gunicorn not available, falling back to Flask development server")
            flask_app.run(host="0.0.0.0", port=port, debug=False)