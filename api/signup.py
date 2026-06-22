import os, json, smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = "autho369@gmail.com"
FROM_NAME = "CallNowService"
# Set this in Vercel environment variables: GMAIL_APP_PASSWORD
GMAIL_PASS = os.environ.get("GMAIL_APP_PASSWORD", "")

def send_email(to, subject, body):
    if not GMAIL_PASS:
        return False
    msg = MIMEText(body)
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to
    msg["Subject"] = subject
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(FROM_EMAIL, GMAIL_PASS)
        server.send_message(msg)
    return True

def handler(request):
    if request.get("method") != "POST":
        return {"statusCode": 405, "body": "Method not allowed"}
    
    try:
        data = json.loads(request.get("body", "{}"))
    except:
        return {"statusCode": 400, "body": "Invalid JSON"}
    
    name = data.get("name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")
    service = data.get("service", "")
    city = data.get("city", "")
    plan = data.get("plan", "")

    # Email to Mirsad
    send_email(
        "autho369@gmail.com",
        f"NEW SIGNUP: {service} - {city}",
        f"New provider signup!\n\nService: {service}\nCity: {city}\nCompany: {name}\nEmail: {email}\nPhone: {phone}\nPlan: {plan}\n\nReview at: https://callnowservice.com/dashboard"
    )
    
    # Confirmation email to provider
    send_email(
        email,
        f"CallNowService - {city} {service} listing received",
        f"Hi {name},\n\nThank you for applying to CallNowService.com!\n\nYour application for {service} in {city} has been received. We will review your business and reach out within 24 hours to verify your details and arrange payment.\n\nPlan selected: {plan}\n\nImportant: Only 5 spots per service per city. Your application is time-stamped and processed in order.\n\nQuestions? Call us at (847) 652-2338.\n\n- Mirsad\n  Founder, CallNowService.com\n  (847) 652-2338"
    )
    
    return {
        "statusCode": 200,
        "body": json.dumps({"success": True, "message": "Application received. Check your email."})
    }
