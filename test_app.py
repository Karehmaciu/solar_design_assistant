import pytest
from app import create_app
import os
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
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

@patch('openai.OpenAI')
def test_prompt_submission(mock_openai, client):
    """Test submitting a prompt and getting a response."""
    # Setup the mock
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test AI response"
    mock_client.chat.completions.create.return_value = mock_response
    
    # Submit a test prompt
    response = client.post('/', data={'prompt': 'Test prompt'})
    
    # Verify the response
    assert response.status_code == 200
    assert b'Test AI response' in response.data

def test_view_report(client):
    """Test the report viewing page."""
    with client.session_transaction() as session:
        session['response_text'] = 'Test report content'
    
    response = client.get('/view-report')
    assert response.status_code == 200
    assert b'Test report content' in response.data

def test_download_report_no_content(client):
    """Test download report when no content is available."""
    # Clear the session to ensure no response text
    client.get('/clear')
    
    # Try to download a report
    response = client.get('/download-report')
    assert response.status_code == 302  # Should redirect