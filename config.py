import os
import secrets
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv("FLASK_SECRET") or "dev-key-NOT-FOR-PRODUCTION-USE"
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=4)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    # Update path to use the existing file in the prompts folder
    PROMPT_PATH = "prompts/kbs_solar_prompt_final.txt"
    # Add a fallback prompt path for guardrails
    GUARDRAILS_PATH = "prompts/solar_pv_chatbot_guardrails.txt"
    TEMPLATE_PATH = "prompts/proreport_template.md"  # Path for ProReport Markdown template

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    # Use a predictable key for testing
    SECRET_KEY = "testing-key-not-for-production"

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    # Consider more restrictive settings for production
    # PREFERRED_URL_SCHEME = "https"

# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

def get_config(config_name=None):
    """Helper function to get configuration"""
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'default')
    return config.get(config_name, config["default"])