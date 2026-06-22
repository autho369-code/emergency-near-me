#!/usr/bin/env python3
"""
Send confirmation email to approved provider
Usage: python confirm_signup.py <provider_email> <provider_name> <service> <city> <plan>
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from send_email import send_email

if len(sys.argv) < 6:
    print("Usage: python confirm_signup.py <email> <name> <service> <city> <plan>")
    print("Example: python confirm_signup.py bob@plumbing.com 'Bob' Plumber Chicago 'Starter - $99/mo'")
    sys.exit(1)

email, name, service, city, plan = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]

subject = f"CallNowService — Your {city} {service} listing is approved!"

body = f"""Hi {name},

Great news! Your application for {service} in {city} has been approved.

Your plan: {plan}
Your listing: https://callnowservice.com

NEXT STEP — PAYMENT
To activate your listing, complete payment here:
https://paypal.me/CallNowService

Once payment is received, your listing goes live within 24 hours and calls start coming to your phone.

Questions? Call me at (847) 652-2338.

- Mirsad
  Founder, CallNowService.com
  (847) 652-2338
"""

result = send_email(email, subject, body)
if result.get("status") == "sent":
    print(f"Confirmation sent to {name} <{email}>")
    print(f"Subject: {subject}")
else:
    print(f"Error: {result.get('error', 'unknown')}")
