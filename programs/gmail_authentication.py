from __future__ import annotations
import os
from typing import Optional, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.message import EmailMessage
import logging

log_dir = "../weather_app/files/programs_files"
os.makedirs(log_dir, exist_ok=True)  # Ensure the directory exists
logging.basicConfig(
        filename=f"{log_dir}/weather_app.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s"
    )



# Minimal scope to send email
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]  # Only send access source: https://developers.google.com/workspace/gmail/api/auth/scopes?hl=en


class GmailAPIAuthentication:
    """
    GmailSender wraps Gmail API authentication.

    Args:
        credentials_path: Path to OAuth 2.0 client credentials JSON downloaded from Google Cloud.
        token_path: Path to store the user's access/refresh token (created after first run).
        user_id: Gmail user id. Use "me" to indicate the authenticated user.
    """

    def __init__(
        self,
        credentials_path: str = "../weather_app/files/config_files/credentials.json",
        token_path: str = "../weather_app/files/config_files/token.json",
        user_id: str = "me",
    ) -> None:
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.user_id = user_id
        self.creds: Optional[Credentials] = None
        self.service = None
        self._ensure_authenticated()

    def _ensure_authenticated(self) -> None:
        """
        Loads credentials from token_path if present, refreshes if necessary,
        or runs an interactive flow to acquire new credentials.
        """
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If no (valid) credentials available, let user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None # If refresh fails, we'll need to log in again
            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"OAuth client credentials not found at {self.credentials_path}. "
                        "Download from Google Cloud Console and save to that location."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_path, "w") as token_file:
                token_file.write(creds.to_json())

        self.creds = creds
        self.service = build("gmail", "v1", credentials=self.creds, cache_discovery=False)

class Gmail_Sender:
    def __init__(self, auth: GmailAPIAuthentication) -> None:
        self.service = auth.service
        self.user_id = auth.user_id
    
    def send_email(self, to: str, subject: str, body_html: str, attachments: Optional[List[str]] = None) -> dict:
        message = EmailMessage()
        message.add_alternative(body_html, subtype='html')
        message['To'] = to
        message['From'] = self.user_id
        message['Subject'] = subject

        # Attach files if any
        if attachments:
            for file_path in attachments:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    file_name = os.path.basename(file_path)
                    message.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {'raw': raw_message}
        sent_message = self.service.users().messages().send(userId=self.user_id, body=send_message).execute()
        return sent_message