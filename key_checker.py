import os
import sys
from dotenv import load_dotenv
import secrets
import openai
from flask import Flask

def check_keys():
    print("Key Availability Check")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"OpenAI API Key: ✅ Available (starts with {openai_key[:4]}...)")
        
        # Try to initialize the client to verify the key
        try:
            if hasattr(openai, 'OpenAI'):
                # New OpenAI client (v1.0.0+)
                client = openai.OpenAI(api_key=openai_key)
                # Try a simple models list call
                models = client.models.list()
                print("OpenAI API Connection: ✅ Working")
            else:
                # Legacy client
                openai.api_key = openai_key
                models = openai.Model.list()
                print("OpenAI API Connection: ✅ Working (legacy client)")
                
            print(f"Available models: {len(models.data)} models found")
            
        except Exception as e:
            print(f"OpenAI API Connection: ❌ Error: {str(e)}")
    else:
        print("OpenAI API Key: ❌ Not available in environment variables")
    
    # Check Flask secret key
    flask_secret = os.getenv("FLASK_SECRET")
    if flask_secret:
        print(f"Flask Secret Key: ✅ Available (starts with {flask_secret[:4]}...)")
        
        # Verify Flask can initialize with the key
        try:
            app = Flask(__name__)
            app.config['SECRET_KEY'] = flask_secret
            # If no error, it's working
            print("Flask Secret Key: ✅ Valid format")
        except Exception as e:
            print(f"Flask Secret Key: ❌ Error: {str(e)}")
    else:
        print("Flask Secret Key: ❌ Not available in environment variables")
        
    # Check if we could generate a secret key if needed
    try:
        fallback_key = secrets.token_hex(16)
        print(f"Fallback Key Generation: ✅ Working (example: {fallback_key[:8]}...)")
    except Exception as e:
        print(f"Fallback Key Generation: ❌ Error: {str(e)}")
        
    print("\nConfig File Check")
    print("=" * 50)
    
    # Check config.py for defaults
    try:
        sys.path.append(os.getcwd())
        from config import get_config
        config = get_config()
        
        print(f"Default config type: {type(config).__name__}")
        print(f"Default SECRET_KEY set: {'✅ Yes' if hasattr(config, 'SECRET_KEY') and config.SECRET_KEY else '❌ No'}")
        print(f"Default OPENAI_API_KEY set: {'✅ Yes' if hasattr(config, 'OPENAI_API_KEY') and config.OPENAI_API_KEY else '❌ No'}")
        print(f"Default OPENAI_MODEL: {getattr(config, 'OPENAI_MODEL', 'Not set')}")
    except Exception as e:
        print(f"Config file check error: {str(e)}")
    
    print("\nRecommendations")
    print("=" * 50)
    
    if not openai_key:
        print("- Add OPENAI_API_KEY to your .env file or environment variables")
    
    if not flask_secret:
        print("- Add FLASK_SECRET to your .env file or environment variables")
        print("  Generate with: python -c \"import secrets; print(secrets.token_hex(32))\"")
        
    print("\nFinished checking keys.")

if __name__ == "__main__":
    check_keys()