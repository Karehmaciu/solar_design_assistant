import os
import sys
from waitress import serve
from app import create_app

def run_server():
    # Create the Flask application
    app = create_app('production')
    
    # Use port 8003 to match your previous configuration
    port = int(os.environ.get("PORT", 8003))
    
    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Print startup message
    print("="*60)
    print(f"Solar Assistant is starting on http://localhost:{port}")
    print("="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60)
    
    try:
        # Run with waitress
        serve(app, host='0.0.0.0', port=port, threads=4)
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_server()