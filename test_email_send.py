import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -----------------------------
# ⚡ Configuration (change here if needed)
# -----------------------------
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USER = 'bas81r1t@gmail.com'
EMAIL_PASSWORD = 'dxagtxtqfesjcyof'  # Gmail App Password
TO_EMAIL = 'bas81r1t@gmail.com'      # test ke liye apne aap ko bhej rahe hain

# -----------------------------
# ✉️ Email content
# -----------------------------
subject = "✅ Test Email from Basharat Movies Hub"
body = "This is a test email to confirm that SMTP email sending works on deployed server."

# Create message
msg = MIMEMultipart()
msg['From'] = EMAIL_USER
msg['To'] = TO_EMAIL
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

# -----------------------------
# 📤 Send email
# -----------------------------
try:
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
    print("✅ Test email sent successfully! Check your inbox/spam folder.")
except Exception as e:
    print("❌ Could not send test email.")
    print("Error:", e)
