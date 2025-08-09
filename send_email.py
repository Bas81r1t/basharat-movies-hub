import yagmail
import os
import sqlite3

def get_refreshed_movie_count():
    conn = sqlite3.connect('db.sqlite3')   # Database file ka naam
    cursor = conn.cursor()
    # Assuming aapke movies table me 'is_refreshed' column hai jisme 1 ho to refresh hua hai
    cursor.execute("SELECT COUNT(*) FROM movies WHERE is_refreshed = 1")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def send_email():
    receiver = "bas81r1t@gmail.com"  # Jis email par bhejna hai
    subject = "Movies Link Refresh Report"
    refreshed_count = get_refreshed_movie_count()
    body = f"Abhi tak total {refreshed_count} movies ki links refresh ho chuki hain."

    gmail_user = os.getenv("GMAIL_USERNAME")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")

    yag = yagmail.SMTP(gmail_user, gmail_app_password)
    yag.send(to=receiver, subject=subject, contents=body)
    print("Email sent successfully!")

if __name__ == "__main__":
    send_email()
