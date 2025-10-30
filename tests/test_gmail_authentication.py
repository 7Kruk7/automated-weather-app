import pytest
import os
import json
import base64
from unittest.mock import patch, MagicMock, mock_open
from email.message import EmailMessage
from os import path, join

from gmail_authentication import GmailAPIAuthentication, Gmail_Sender

@pytest.fixture
def fake_creds():
    """Fake credentials object with minimal interface."""
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.expired = False
    mock_creds.refresh_token = None
    mock_creds.to_json.return_value = json.dumps({"token": "fake-token"})
    return mock_creds

@pytest.fixture
def fake_service():
    """Fake Gmail API service."""
    mock_service = MagicMock()
    mock_messages = mock_service.users().messages()
    mock_messages.send().execute.return_value = {"id": "12345", "labelIds": ["SENT"]}
    return mock_service


def test_auth_uses_existing_valid_token(tmp_path, fake_creds, fake_service):
    '''Test that existing valid token is used without re-authentication.'''
    token_path = os.path.join(tmp_path, "token.json")
    token_path.write_text(fake_creds.to_json())

    with patch("gmail_authentication.Credentials.from_authorized_user_file", return_value=fake_creds), \
         patch("your_module.build", return_value=fake_service):
        auth = GmailAPIAuthentication(
            credentials_path=str(tmp_path / "credentials.json"),
            token_path=str(token_path)
        )

    assert auth.creds.valid is True
    assert auth.service is fake_service