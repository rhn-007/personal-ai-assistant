class EmailIntegration:
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

    def __init__(self):
        self.service = None
        self._authenticate()

    # =====================================================
    # BASIC EMAIL FETCHING
    # =====================================================

    def get_emails(self, query="is:unread", max_results=5):
        if not self.service:
            return []

        results = self.service.users().messages().list(
            userId="me",
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get("messages", [])

        emails = []
        for msg in messages:
            email = self._get_email(msg["id"])
            if email:
                emails.append(email)

        return emails

    def get_unread_emails(self):
        return self.get_emails("is:unread")

    def get_latest_email(self):
        emails = self.get_emails("in:inbox", 1)
        return emails[0] if emails else None

    def search_emails(self, query: str):
        return self.get_emails(query)

    # =====================================================
    # EMAIL DETAILS
    # =====================================================

    def _get_email(self, message_id):
        msg = self.service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute()

        headers = msg.get("payload", {}).get("headers", [])

        def get_header(name):
            return next((h["value"] for h in headers if h["name"] == name), "")

        return {
            "id": message_id,
            "subject": get_header("Subject"),
            "from": get_header("From"),
            "to": get_header("To"),
            "date": get_header("Date")
        }

    # =====================================================
    # SEND EMAIL
    # =====================================================

    def send_email(self, to, subject, body):
        from email.mime.text import MIMEText
        import base64

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        self.service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

        return True

    # =====================================================
    # FUTURE ACTIONS (PLACEHOLDERS FOR STAGE 2)
    # =====================================================

    def delete_email(self, message_id):
        self.service.users().messages().delete(
            userId="me",
            id=message_id
        ).execute()
        return True

    def mark_as_read(self, message_id):
        self.service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        return True

    def archive_email(self, message_id):
        self.service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["INBOX"]}
        ).execute()
        return True
