"""
IMAP email scanner for CallNow Intake Agent.
Run via: python references/imap-check.py
Reads autho369@gmail.com inbox, finds provider replies and inquiries.
"""

import os, imaplib, email, json
from email.header import decode_header
from datetime import datetime, timedelta

# --- Credentials: read .env without shell (shell 'source' breaks on special chars) ---
env_path = r'C:\Users\autho\emergency-near-me\.env'
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        eq = line.find('=')
        if eq < 0:
            continue
        key = line[:eq]
        val = line[eq + 1:].strip().strip('"').strip("'")
        os.environ[key] = val

pw = os.environ.get('GMAIL_APP_PASSWORD', '')
if len(pw) < 16:
    print(f'BLOCKED: GMAIL_APP_PASSWORD too short ({len(pw)} chars)')
    exit(1)

# --- Connect ---
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('autho369@gmail.com', pw)
mail.select('inbox')

# --- Search recent ---
since = (datetime.now() - timedelta(days=14)).strftime('%d-%b-%Y')
result, data = mail.search(None, f'(SINCE {since})')
email_ids = data[0].split()
print(f'Total emails in 14 days: {len(email_ids)}')

# --- Find replies (In-Reply-To, References, or Re:/RE: subject) ---
replies = []
for eid in email_ids:
    result, msg_data = mail.fetch(eid, '(RFC822)')
    msg = email.message_from_bytes(msg_data[0][1])

    # Check for reply headers
    headers_str = '\n'.join(f'{k}: {v}' for k, v in msg.items())
    has_in_reply_to = 'In-Reply-To:' in headers_str or 'References:' in headers_str

    subj = decode_header(msg['Subject'])[0][0]
    if isinstance(subj, bytes):
        subj = subj.decode(errors='replace')
    has_re_subj = (subj or '').lower().startswith('re:')

    if has_in_reply_to or has_re_subj:
        # Extract plain-text body
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode(errors='replace')
                    except Exception:
                        pass
                    break
        else:
            try:
                body = msg.get_payload(decode=True).decode(errors='replace')
            except Exception:
                pass

        replies.append({
            'id': eid.decode(),
            'from': msg['From'],
            'subject': subj,
            'date': msg['Date'],
            'body': body.strip()[:2000],
        })

print(f'\nReplies found: {len(replies)}')
for r in replies:
    print(f"  {r['id']} | {r['from']} | {r['subject']} | {r['date']}")

# --- Find non-newsletter emails (potential direct inquiries) ---
skip_domains = [
    'news.', 'email.', 'mail.', 'marketing.', 'engage.', 'notification',
    'noreply', 'no-reply', 'notifications@', 'invoice+', 'bounce', 'reply@',
    'accounts.google.com', 'github.com', 'stripe.com', 'supabase', 'vercel',
    'twilio', 'tiktok', 'etsy', 'canva', 'microsoft', 'openai', 'redhat',
    'workspace', 'payments', 'google.com', 'deepseek', 'factory.ai',
    'similarweb', 'vistaprint', 'buildasign', 'imagine', 'rivalflow',
    'framer.com', 'spyfu.com', 'tally.so', 'n8n.io', 'patrickdang.com',
    'team.emergent.sh', 'railway.app', 'veed.io',
]

print('\nNon-automated emails:')
for eid in email_ids:
    result, msg_data = mail.fetch(eid, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
    headers = msg_data[0][1].decode(errors='replace')
    lower = headers.lower()
    if not any(d in lower for d in skip_domains):
        print(f'  {eid.decode()} | {headers[:300]}')

mail.logout()
print('\nDone.')
