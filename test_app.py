import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
import traceback

# Force the secret key and OpenAI key to be set in environment variables
os.environ['FLASK_SECRET'] = 'test-secret-key-for-pytest'
os.environ['OPENAI_API_KEY'] = 'test-openai-key-for-pytest'

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    from app import create_app
    
    # Create app with testing config
    app = create_app("testing")
    
    # Explicitly set crucial config values
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['SECRET_KEY'] = 'test-secret-key-for-pytest'
    app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem session for tests
    
    # Force debug off to mimic production
    app.debug = False
    
    # Return the app for testing
    return app

@pytest.fixture
def client(app):
    """A test client for the app with session support."""
    # Using test_client's context manager to handle setup/teardown
    with app.test_client() as client:
        # Enable cookies for session support
        client.testing = True
        client.cookie_jar.clear()
        
        # Push an application context to ensure sessions work
        with app.app_context():
            yield client

# Create a mock OpenAI client that doesn't depend on SDK version
class MockOpenAI:
    class ChatCompletions:
        @staticmethod
        def create(*args, **kwargs):
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="Test AI response")
                    )
                ]
            )
    
    chat = SimpleNamespace(completions=ChatCompletions())

# Register our mock before importing app
sys.modules['openai'] = MagicMock()
sys.modules['openai'].OpenAI = MockOpenAI
sys.modules['openai'].ChatCompletion = MockOpenAI.ChatCompletions
sys.modules['openai'].chat = MockOpenAI.chat

def test_index_get(client):
    """Test that the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Solar Assistant' in response.data

def test_clear_session(client):
    """Test the clear session functionality."""
    # Set session data directly
    with client.session_transaction() as session:
        session['response_text'] = 'Test response'
    
    # Make request to clear session
    response = client.get('/clear')
    assert response.status_code == 302  # Redirect
    
    # Verify session was cleared
    with client.session_transaction() as session:
        assert 'response_text' not in session

# Use our already registered mock instead of patching
def test_prompt_submission(client):
    """Test submitting a prompt and getting a response."""
    response = client.post('/', data={
        'prompt': 'Test prompt with sufficient length',
        'language': 'en',
        'csrf_token': 'test-token'  # Mock csrf token
    }, follow_redirects=True)
    
    # Check the response
    assert response.status_code == 200
    assert b"Test AI response" in response.data

def test_view_report(client):
    """Test the report viewing page."""
    with client.session_transaction() as session:
        session['response_text'] = 'Test report content'
    
    response = client.get('/view-report')
    assert response.status_code == 200
    assert b'Test report content' in response.data

def test_download_report_no_content(client):
    """Test download report when no content is available."""
    # Clear any existing session
    with client.session_transaction() as session:
        if 'response_text' in session:
            del session['response_text']
    
    # Try to download a report when no content is available
    response = client.get('/download-report')
    assert response.status_code == 302  # Should redirect