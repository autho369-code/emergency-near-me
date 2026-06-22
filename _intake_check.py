import os, imaplib, email, json
from email.header import decode_header
from datetime import datetime, timedelta

# Load .env file
env_path = r'C:\Users\autho\emergency-near-me\.env'
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        eq = line.find('=')
        if eq < 0:
            continue
        key = line[:eq]
        val = line[eq+1:].strip().strip('"').strip("'")
        os.environ[key] = val

pw = os.environ.get('GMAIL_APP_PASSWORD', '')
print(f'PW length: {len(pw)}')
if len(pw) < 16:
    print('BLOCKED: GMAIL_APP_PASSWORD too short')
    exit(1)

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('autho369@gmail.com', pw)
mail.select('inbox')

since = (datetime.now() - timedelta(days=14)).strftime('%d-%b-%Y')
result, data = mail.search(None, f'(SINCE {since})')
email_ids = data[0].split()

print(f'Total emails in 14 days: {len(email_ids)}')

# Find replies
replies = []
for eid in email_ids:
    result, msg_data = mail.fetch(eid, '(RFC822)')
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    
    headers_str = ''
    for k, v in msg.items():
        headers_str += f'{k}: {v}\n'
    
    has_reply = 'In-Reply-To:' in headers_str or 'References:' in headers_str
    subj = decode_header(msg['Subject'])[0][0]
    if isinstance(subj, bytes):
        subj = subj.decode(errors='replace')
    has_re_subj = (subj or '').startswith('Re:') or (subj or '').startswith('RE:')
    
    if has_reply or has_re_subj:
        sender = msg['From']
        date = msg['Date']
        
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode(errors='replace')
                    except:
                        pass
                    break
        else:
            try:
                body = msg.get_payload(decode=True).decode(errors='replace')
            except:
                pass
        
        replies.append({
            'id': eid.decode(),
            'from': sender,
            'subject': subj,
            'date': date,
            'body': body[:1000]
        })
        print(f'\nREPLY #{len(replies)}: {eid.decode()}')
        print(f'From: {sender}')
        print(f'Subject: {subj}')
        print(f'Date: {date}')
        print(f'Body: {body[:500]}')

print(f'\nTotal replies: {len(replies)}')

# Non-automated emails
print('\n--- NON-AUTOMATED EMAILS ---')
skip = ['news.', 'email.', 'mail.', 'marketing.', 'engage.', 'notification',
        'noreply', 'no-reply', 'notifications@', 'invoice+', 'bounce', 'reply@',
        'accounts.google.com', 'github.com', 'stripe.com', 'supabase', 'vercel',
        'twilio', 'tiktok', 'etsy', 'canva', 'microsoft', 'openai', 'redhat',
        'workspace', 'payments', 'google.com', 'deepseek', 'factory.ai',
        'similarweb', 'vistaprint', 'buildasign', 'imagine', 'rivalflow']
inquiries = []
for eid in email_ids:
    result, msg_data = mail.fetch(eid, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
    headers = msg_data[0][1].decode(errors='replace')
    lower = headers.lower()
    if not any(d in lower for d in skip):
        subj_start = headers.find('Subject:')
        from_start = headers.find('From:')
        date_start = headers.find('Date:')
        subj = headers[subj_start:subj_start+150] if subj_start >= 0 else ''
        frm = headers[from_start:from_start+100] if from_start >= 0 else ''
        inquiries.append(f'{eid.decode()}|{frm.strip()}|{subj.strip()}')
        print(f'{eid.decode()}|{frm.strip()}|{subj.strip()}')

print(f'\nNon-automated: {len(inquiries)}')
mail.logout()
