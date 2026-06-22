#!/usr/bin/env python3
"""Intake Agent: Check Gmail for provider replies via IMAP."""
import imaplib
import email
import json
import os
import re
import sys
from datetime import datetime, timedelta
from email.header import decode_header

# --- Load .env safely (Python, not shell) ---
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
creds = {}
try:
    with open(env_path, 'r') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            eq_idx = line.find('=')
            if eq_idx == -1:
                continue
            k = line[:eq_idx].strip()
            v = line[eq_idx + 1:].strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            if v.startswith("'") and v.endswith("'"):
                v = v[1:-1]
            creds[k] = v
except Exception as e:
    print(json.dumps({"error": f"Failed to read .env: {e}"}))
    sys.exit(1)

GMAIL_USER = creds.get('GMAIL_USER', 'autho369@gmail.com')
GMAIL_APP_PASSWORD = creds.get('GMAIL_APP_PASSWORD', '')

if not GMAIL_APP_PASSWORD:
    print(json.dumps({"error": "GMAIL_APP_PASSWORD not found in .env"}))
    sys.exit(1)

# --- Newsletter domains to skip ---
NEWSLETTER_DOMAINS = {
    'mailchimp', 'sendgrid.net', 'mandrillapp.com', 'mailgun',
    'amazonses.com', 'constantcontact', 'campaignmonitor',
    'litmus.com', 'hubspot', 'marketo', 'activecampaign',
    'convertkit', 'klaviyomail', 'drip', 'mailerlite',
    'bounce', 'noreply', 'no-reply', 'donotreply',
    'notification', 'alerts', 'updates@', 'newsletter',
    'linkedin.com', 'facebookmail.com', 'twitter.com',
    'instagram.com', 'pinterest', 'tiktok',
    'quora.com', 'reddit.com', 'medium.com', 'substack',
    'youtube.com', 'google.com'  # generic google notifications
}

# --- IMAP connection ---
try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
except Exception as e:
    print(json.dumps({"error": f"IMAP login failed: {e}"}))
    sys.exit(1)

mail.select('INBOX')

# Search last 14 days
since_date = (datetime.now() - timedelta(days=14)).strftime('%d-%b-%Y')
status, messages = mail.search(None, f'(SINCE {since_date})')
if status != 'OK':
    print(json.dumps({"error": f"IMAP search failed: {status}"}))
    sys.exit(1)

msg_ids = messages[0].split()
results = []

# Also check trash/spam for potential signups
for folder in ['INBOX', '[Gmail]/Spam']:
    if folder != 'INBOX':
        try:
            mail.select(folder)
        except:
            continue
        status, msgs = mail.search(None, f'(SINCE {since_date})')
        if status != 'OK':
            continue
        msg_ids = list(set(msg_ids) | set(msgs[0].split()))

mail.select('INBOX')

processed = 0
provider_leads = []

# Process most recent first
for msg_id in reversed(msg_ids[-200:]):  # Process up to 200 most recent
    if processed >= 50:  # Safety cap
        break
    try:
        status, msg_data = mail.fetch(msg_id, '(RFC822)')
        if status != 'OK':
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject_raw = msg.get('Subject', '')
        subject_parts = decode_header(subject_raw)
        subject = ''
        for part, charset in subject_parts:
            if isinstance(part, bytes):
                subject += part.decode(charset or 'utf-8', errors='replace')
            else:
                subject += str(part)

        sender = msg.get('From', '')
        # Extract email address
        sender_email = ''
        sender_name = ''
        if '<' in sender:
            sender_name = sender.split('<')[0].strip().strip('"').strip("'")
            sender_email = sender.split('<')[1].split('>')[0].strip()
        else:
            sender_email = sender.strip()

        # Skip newsletters
        sender_domain = sender_email.split('@')[-1].lower() if '@' in sender_email else ''
        is_newsletter = False
        for nd in NEWSLETTER_DOMAINS:
            if nd.lower() in sender_domain.lower() or nd.lower() in sender_email.lower():
                is_newsletter = True
                break

        # Check for Re: / reply indicators
        in_reply_to = msg.get('In-Reply-To', '')
        references = msg.get('References', '')
        is_reply = bool(in_reply_to or references or subject.lower().startswith('re:'))

        # Check for known outreach recipients (providers we've emailed)
        is_provider = False

        # Check if this is a reply to one of our outreach emails
        message_id = msg.get('Message-ID', '')
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='replace')
                    except:
                        body += str(part.get_payload())
                elif content_type == 'text/html':
                    continue  # Prefer plain text
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='replace')
            except:
                body = str(msg.get_payload())

        # Determine if this is likely a provider inquiry
        # Signals: reply to us, or contains service-related keywords in body
        service_keywords = [
            'plumber', 'electrician', 'hvac', 'roofer', 'locksmith',
            'mechanic', 'appliance', 'plumbing', 'electrical', 'heating',
            'cooling', 'air conditioning', 'roofing', 'repair',
            'listing', 'signup', 'sign up', 'register', 'join',
            'callnow', 'call now', 'emergency', 'near me',
            'provider', 'service', 'contractor', 'business',
            'lead', 'leads', 'customer', 'interested'
        ]
        body_lower = body.lower()
        subject_lower = subject.lower()
        keyword_hits = [kw for kw in service_keywords if kw in body_lower or kw in subject_lower]

        is_provider = is_reply or (len(keyword_hits) >= 2 and not is_newsletter)

        if not is_provider:
            continue

        # --- Extract provider details ---
        # Try to find phone numbers in body
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\+\d{1,2}\s*\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',
        ]
        phone = ''
        for pat in phone_patterns:
            m = re.search(pat, body)
            if m:
                phone = m.group(0)
                break

        # Try to find website
        website = ''
        web_match = re.search(r'(https?://[^\s<>"]+)', body)
        if web_match:
            website = web_match.group(1).rstrip('.,;:')

        # Try to identify city
        city_hints = re.findall(r'(?:in|near|from|serve|based in|located in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})', body)
        city = city_hints[0] if city_hints else ''

        # Determine response category
        category = 'new_inquiry'
        if 'interested' in body_lower or 'sign up' in body_lower or 'join' in body_lower:
            category = 'interested'
        elif 'tell me more' in body_lower or 'more info' in body_lower or 'pricing' in body_lower:
            category = 'tell_me_more'
        elif 'not interested' in body_lower or 'unsubscribe' in body_lower:
            category = 'not_interested'
        elif 'wrong' in body_lower:
            category = 'wrong_service'

        provider = {
            'name': sender_name or sender_email,
            'email': sender_email,
            'service_type': keyword_hits[0] if keyword_hits else 'unknown',
            'city': city,
            'phone': phone,
            'website': website,
            'subject': subject,
            'body_snippet': body[:500],
            'date': msg.get('Date', ''),
            'category': category,
            'priority': 'HIGH' if category in ('interested',) else ('MEDIUM' if category == 'tell_me_more' else 'LOW'),
            'is_reply': is_reply,
            'message_id': msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
        }
        provider_leads.append(provider)
        processed += 1

    except Exception as e:
        continue

mail.logout()

# Output as JSON
output = {
    'status': 'ok',
    'emails_scanned': len(msg_ids),
    'providers_found': len(provider_leads),
    'providers': provider_leads,
}

print(json.dumps(output, indent=2, ensure_ascii=False))
