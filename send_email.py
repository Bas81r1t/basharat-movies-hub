import yagmail
import os

def send_email():
    receiver = "bas81r1t@gmail.com"  # Jis email par report bhejni hai
    subject = "GitHub Actions Report"
    body = "Yeh aapki GitHub Actions workflow se bheji gayi email report hai."

    gmail_user = os.getenv("GMAIL_USERNAME")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")

    yag = yagmail.SMTP(gmail_user, gmail_app_password)
    yag.send(to=receiver, subject=subject, contents=body)
    print("Email sent successfully!")

if __name__ == "__main__":
    send_email()
