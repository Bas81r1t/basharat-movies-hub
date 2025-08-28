import os
import django
from django.core.mail import send_mail
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basharat.settings')
django.setup()

subject = "📬 Test Email from Basharat Movies Hub"
message = "✅ This is a test email. If you received this, SMTP is working!"
from_email = os.getenv('EMAIL_HOST_USER')
to_email = [os.getenv('EMAIL_HOST_USER')]

try:
    send_mail(subject, message, from_email, to_email, fail_silently=False)
    print("✅ Test email sent successfully! Check your inbox/spam folder.")
except Exception as e:
    print("❌ Email send failed:", e)
