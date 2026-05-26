import boto3
from botocore.exceptions import ClientError
import os
from typing import Optional

class Mailer:
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode or os.getenv('DEBUG', 'false').lower() == 'true'
        
        if not self.debug_mode:
            self.ses_client = boto3.client(...)
        # ...
    
    async def send_reset_email(self, email: str, token: str) -> None:
        reset_link = f"{self.base_url}/reset-password?token={token}"
        
        if self.debug_mode:
            # Original debug behavior
            print(f"[MAILER] Send reset email to {email}")
            print(f"[MAILER] Link: {reset_link}")
            return
        
        # ... actual SES sending code


"""
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
SENDER_EMAIL=noreply@management.com
APP_BASE_URL=https://management.com

pip install boto3
"""