#!/usr/bin/env python3
"""
SendGrid email sender for CallNowService
Usage: python send_email.py <to_email> <subject> <body_text>
API key read from environment: SENDGRID_API_KEY
"""

import os, sys, json, urllib.request, urllib.error

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
FROM_EMAIL = "hello@callservicenow.com"
FROM_NAME = "CallNowService"

def send_email(to_email, subject, body, api_key=None):
    key = api_key or SENDGRID_API_KEY
    if not key:
        return {"error": "SENDGRID_API_KEY not set"}
    
    data = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": FROM_EMAIL, "name": FROM_NAME},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}]
    }
    
    req = urllib.request.Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            return {"status": resp.status, "sent": True, "to": to_email, "subject": subject}
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode())
        return {"error": str(e.code), "detail": err}

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python send_email.py <to> <subject> <body>")
        sys.exit(1)
    
    result = send_email(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(result, indent=2))
