import pytest
from app import create_app
import os
from unittest.mock import patch, MagicMock
from types import SimpleNamespace

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    os.environ['OPENAI_API_KEY'] = 'test-key'
    os.environ['FLASK_SECRET'] = 'test-secret-key'
    app = create_app("testing")
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

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

# Create a dummy completion object that mimics OpenAI's response structure
dummy_completion = SimpleNamespace(
    choices=[
        SimpleNamespace(
            message=SimpleNamespace(content="Test AI response")
        )
    ]
)

@patch("openai.resources.chat.completions.Completions.create", return_value=dummy_completion)
def test_prompt_submission(mock_create, client):
    """Test submitting a prompt and getting a response."""
    response = client.post('/', data={
        'prompt': 'Test prompt',
        'language': 'en'
    })
    
    # Check the response
    assert response.status_code == 200
    formatted_response = "Test AI response".replace('\n', '<br>')
    assert formatted_response.encode() in response.data

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