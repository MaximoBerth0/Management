class Mailer:
    async def send_reset_email(self, email: str, token: str) -> None:
        reset_link = (
            f"https://management.com/reset-password"
            f"?token={token}"
        )

        # DEV / DEBUG
        print(f"[MAILER] Send reset email to {email}")
        print(f"[MAILER] Link: {reset_link}")
