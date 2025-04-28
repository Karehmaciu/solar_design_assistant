import pytest
from app import create_app
import os
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
import openai
import traceback

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Set environment variables for testing
    os.environ['OPENAI_API_KEY'] = 'test-key'
    os.environ['FLASK_SECRET'] = 'test-secret-key'
    
    # Create app with testing config
    app = create_app("testing")
    
    # Configure the app for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SERVER_NAME'] = 'localhost'  # Required for url_for in tests
    
    # Yield the app for testing
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_index_get(client):
    """Test that the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Solar Assistant' in response.data

def test_clear_session(client):
    """Test the clear session functionality."""
    with client.session_transaction() as session:
        session['response_text'] = 'Test response'
    
    response = client.get('/clear')
    assert response.status_code == 302  # Redirect
    
    with client.session_transaction() as session:
        assert 'response_text' not in session

# Check if newer OpenAI SDK is available
has_openai_client = hasattr(openai, "OpenAI")

# Create a patch target based on OpenAI SDK version
if has_openai_client:
    mock_target = "openai.resources.chat.completions.Completions.create"
else:
    mock_target = "openai.ChatCompletion.create"

# Create a dummy completion object that mimics OpenAI's response structure
# This works for both SDK versions
dummy_completion = SimpleNamespace(
    choices=[
        SimpleNamespace(
            message=SimpleNamespace(content="Test AI response")
        )
    ]
)

@patch(mock_target, return_value=dummy_completion)
def test_prompt_submission(mock_create, client):
    """Test submitting a prompt and getting a response."""
    try:
        response = client.post('/', data={
            'prompt': 'Test prompt',
            'language': 'en'
        })
        
        # Check the response
        assert response.status_code == 200
        formatted_response = "Test AI response".replace('\n', '<br>')
        assert formatted_response.encode() in response.data
    except Exception as e:
        pytest.fail(f"Test failed with exception: {str(e)}\n{traceback.format_exc()}")

def test_view_report(client):
    """Test the report viewing page."""
    with client.session_transaction() as session:
        session['response_text'] = 'Test report content'
    
    response = client.get('/view-report')
    assert response.status_code == 200
    assert b'Test report content' in response.data

def test_download_report_no_content(client):
    """Test download report when no content is available."""
    # Try to download a report without setting session content
    response = client.get('/download-report')
    assert response.status_code == 302  # Should redirect