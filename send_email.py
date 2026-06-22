#!/usr/bin/env python3
"""
Gmail SMTP email sender for CallNowService
Send up to 500 emails/day via Gmail.

Setup: Set GMAIL_APP_PASSWORD environment variable
       Get password at https://myaccount.google.com/apppasswords

Usage: python send_email.py <to_email> <subject> <body_text>
"""

import os, sys, smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = "autho369@gmail.com"
FROM_NAME = "CallNowService"

def send_email(to_email, subject, body, password=None):
    pw = password or os.environ.get("GMAIL_APP_PASSWORD", "")
    if not pw:
        return {"error": "GMAIL_APP_PASSWORD not set"}
    
    msg = MIMEText(body)
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(FROM_EMAIL, pw)
            server.send_message(msg)
        return {"status": "sent", "to": to_email}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python send_email.py <to> <subject> <body>")
        sys.exit(1)
    result = send_email(sys.argv[1], sys.argv[2], sys.argv[3])
    print(result.get("status") or f"Error: {result['error']}")
