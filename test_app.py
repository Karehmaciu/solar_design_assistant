import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
import traceback

# Force the secret key and OpenAI key to be set in environment variables
os.environ['FLASK_SECRET'] = 'test-secret-key-for-pytest'
os.environ['OPENAI_API_KEY'] = 'test-openai-key-for-pytest'

# Create mock results before imports to avoid import errors
mock_model_list = SimpleNamespace(
    data=[
        SimpleNamespace(id="gpt-4"),
        SimpleNamespace(id="gpt-3.5-turbo")
    ]
)

mock_chat_completion = SimpleNamespace(
    choices=[
        SimpleNamespace(
            message=SimpleNamespace(content="Test AI response")
        )
    ]
)

# Create a complete mock of the OpenAI module
class MockOpenAI:
    class ChatCompletions:
        @staticmethod
        def create(*args, **kwargs):
            return mock_chat_completion
    
    class Models:
        @staticmethod
        def list(*args, **kwargs):
            return mock_model_list
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.chat = SimpleNamespace(completions=self.ChatCompletions())
        self.models = self.Models()

# Create mock for legacy API
class MockLegacyAPI:
    @staticmethod
    def list(*args, **kwargs):
        return mock_model_list

# Set up patches for both new and legacy OpenAI APIs
mock_module = MagicMock()
mock_module.OpenAI = MockOpenAI
mock_module.Model = MockLegacyAPI
mock_module.ChatCompletion.create.return_value = mock_chat_completion

# Apply the patch to the sys.modules
sys.modules['openai'] = mock_module

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    from app import create_app
    
    # Create app with testing config
    app = create_app("testing")
    
    # Explicitly set crucial config values
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key-for-pytest'
    app.config['DEBUG'] = False
    
    # Make sure configuration is not overridden in the create_app
    if not app.secret_key or app.secret_key == 'dev-key-NOT-FOR-PRODUCTION-USE':
        app.secret_key = 'test-secret-key-for-pytest'
    
    # Return the app for testing
    yield app

@pytest.fixture
def client(app):
    """A test client for the app with session support."""
    with app.test_client() as client:
        # Enable cookies for session support
        client.testing = True
        
        # Push an application context to ensure sessions work
        with app.app_context():
            # Pre-configure the session with a secret key for testing
            app.config['SESSION_TYPE'] = 'filesystem'
            app.secret_key = 'test-secret-key-for-pytest'
            yield client

def test_index_get(client):
    """Test that the index page loads correctly."""
    try:
        response = client.get('/')
        assert response.status_code == 200
        assert b'Solar Assistant' in response.data
    except Exception as e:
        pytest.fail(f"Test failed with exception: {str(e)}\n{traceback.format_exc()}")

def test_clear_session(client):
    """Test the clear session functionality."""
    try:
        # Set session data directly within app context
        with client.session_transaction() as session:
            session['response_text'] = 'Test response'
        
        # Make request to clear session
        response = client.get('/clear')
        assert response.status_code == 302  # Redirect
        
        # Check session was cleared
        with client.session_transaction() as session:
            assert 'response_text' not in session
    except Exception as e:
        pytest.fail(f"Test failed with exception: {str(e)}\n{traceback.format_exc()}")

def test_prompt_submission(client):
    """Test submitting a prompt and getting a response."""
    try:
        response = client.post('/', data={
            'prompt': 'Test prompt with minimum required length for validation',
            'language': 'en'
        }, follow_redirects=True)
        
        # Check the response
        assert response.status_code == 200
        assert b"Test AI response" in response.data or b"Test response" in response.data
    except Exception as e:
        pytest.fail(f"Test failed with exception: {str(e)}\n{traceback.format_exc()}")

def test_view_report(client):
    """Test the report viewing page."""
    try:
        # Set session data
        with client.session_transaction() as session:
            session['response_text'] = 'Test report content'
        
        response = client.get('/view-report')
        assert response.status_code == 200
        assert b'Test report content' in response.data
    except Exception as e:
        pytest.fail(f"Test failed with exception: {str(e)}\n{traceback.format_exc()}")

def test_download_report_no_content(client):
    """Test download report when no content is available."""
    try:
        # Clear any existing session
        with client.session_transaction() as session:
            if 'response_text' in session:
                del session['response_text']
        
        # Try to download a report when no content is available
        response = client.get('/download-report')
        assert response.status_code == 302  # Should redirect
    except Exception as e:
        pytest.fail(f"Test failed with exception: {str(e)}\n{traceback.format_exc()}")