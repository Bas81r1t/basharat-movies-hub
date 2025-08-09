import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

BASE_URL = "https://basharat-movies-hub.onrender.com"

# ====== EMAIL CONFIG ======
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")      # GitHub Secrets me store karo
EMAIL_PASS = os.getenv("EMAIL_PASS")      # GitHub Secrets me store karo
TO_EMAIL = os.getenv("TO_EMAIL")          # Jis email pe report bhejni hai

TIMEOUT = 10  # seconds
LAST_LINKS_FILE = "last_links.txt"  # Purane links save karne ke liye

# ===== Helper functions for old/new detection =====
def load_last_links():
    if os.path.exists(LAST_LINKS_FILE):
        with open(LAST_LINKS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f.readlines())
    return set()

def save_current_links(links):
    with open(LAST_LINKS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(links))

# Step 1: Get all playlist pages
def get_playlist_urls():
    playlist_links = []
    try:
        response = requests.get(BASE_URL, timeout=TIMEOUT)
        soup = BeautifulSoup(response.content, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if "/playlist/" in href:
                if href.startswith("http"):
                    playlist_links.append(href)
                else:
                    playlist_links.append(BASE_URL + href)
    except Exception as e:
        print(f"❌ Error fetching main page: {e}")
    return playlist_links

# Step 2: Get movie links from each playlist
def get_movie_links_from_playlists(playlist_urls):
    movie_links = []
    for url in playlist_urls:
        try:
            res = requests.get(url, timeout=TIMEOUT)
            soup = BeautifulSoup(res.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "/movie/" in href:
                    if href.startswith("http"):
                        movie_links.append(href)
                    else:
                        movie_links.append(BASE_URL + href)
        except Exception as e:
            print(f"❌ Error loading playlist {url}: {e}")
    return movie_links

# Step 3: Extract GoFile links from movie detail pages
def extract_gofile_links_from_movie_pages(movie_urls):
    gofile_links = []
    for url in movie_urls:
        try:
            res = requests.get(url, timeout=TIMEOUT)
            soup = BeautifulSoup(res.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "gofile.io/d/" in href:
                    gofile_links.append(href)
        except Exception as e:
            print(f"❌ Error fetching movie page {url}: {e}")
    return gofile_links

# Step 4: Refresh each GoFile link + detect new/old
def refresh_links():
    playlist_urls = get_playlist_urls()
    movie_urls = get_movie_links_from_playlists(playlist_urls)
    gofile_links = extract_gofile_links_from_movie_pages(movie_urls)

    old_links = load_last_links()
    current_links = set(gofile_links)

    new_links = current_links - old_links
    old_refreshed_links = current_links & old_links

    refreshed_count = 0
    failed_links = []

    for link in current_links:
        try:
            r = requests.get(link, timeout=TIMEOUT)
            if r.status_code == 200:
                refreshed_count += 1
            else:
                failed_links.append(link)
        except Exception as e:
            failed_links.append(f"{link} - {e}")

    # Save current links for next run
    save_current_links(current_links)

    return playlist_urls, movie_urls, current_links, refreshed_count, failed_links, new_links, old_refreshed_links

# Step 5: Send email report
def send_email_report(playlists, movies, gofiles, refreshed_count, failed_links, new_links, old_refreshed_links):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    subject = f"GoFile Auto-Refresh Report - {now}"

    body = f"""
📅 Report Time: {now}
📂 Playlists Found: {len(playlists)}
🎬 Movies Found: {len(movies)}
🔗 GoFile Links Found: {len(gofiles)}
✨ New Links Found: {len(new_links)}
♻️ Old Links Refreshed: {len(old_refreshed_links)}
✅ Refreshed Successfully: {refreshed_count}
❌ Failed Links: {len(failed_links)}

New Links List:
{chr(10).join(new_links) if new_links else 'No new links'}

Failed Link Details:
{chr(10).join(failed_links) if failed_links else 'None'}

Regards,  
Basharat Movie Hub Auto-Refresher
"""

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = TO_EMAIL

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())
        server.quit()
        print("📧 Email report sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    playlists, movies, gofiles, refreshed_count, failed_links, new_links, old_refreshed_links = refresh_links()
    send_email_report(playlists, movies, gofiles, refreshed_count, failed_links, new_links, old_refreshed_links)
