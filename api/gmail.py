import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GmailClient:
    def __init__(self, creds):
        self.service = build('gmail', 'v1', credentials=creds)

    def create_draft(self, to_email, subject, body):
        """Creates a draft email."""
        try:
            message = EmailMessage()
            message.set_content(body)
            message['To'] = to_email
            message['Subject'] = subject

            # Encode the message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {
                'message': {
                    'raw': encoded_message
                }
            }

            draft = self.service.users().drafts().create(userId="me", body=create_message).execute()
            return draft
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
