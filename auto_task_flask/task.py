import requests
import time
from bs4 import BeautifulSoup

SITE_URL = "https://basharat-movies-hub.onrender.com"
GOFILE_BASE = "https://gofile.io/d/"


def get_playlist_links():
    try:
        res = requests.get(SITE_URL, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        playlist_links = [
            SITE_URL + a["href"] for a in soup.find_all("a", href=True)
            if a["href"].startswith("/playlist/")
        ]
        return playlist_links
    except Exception as e:
        print(f"❌ Error getting playlists: {e}")
        return []


def get_movie_links_from_playlist(playlist_url):
    try:
        res = requests.get(playlist_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        return [
            SITE_URL + a["href"]
            for a in soup.find_all("a", href=True, class_="title-link")
            if a["href"].startswith("/movie/")
        ]
    except Exception as e:
        print(f"⚠️ Failed to load playlist {playlist_url}: {e}")
        return []


def extract_gofile_link(detail_url):
    try:
        res = requests.get(detail_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            if GOFILE_BASE in a["href"]:
                return a["href"]
        return None
    except:
        return None


def refresh_link(url):
    try:
        r = requests.head(url, timeout=10)
        return r.status_code == 200
    except:
        return False


def run_refresh_job():
    all_movie_pages = []

    playlists = get_playlist_links()
    for pl in playlists:
        print(f"📂 Checking playlist: {pl}")
        movie_pages = get_movie_links_from_playlist(pl)
        all_movie_pages.extend(movie_pages)

    print(f"🎬 Total movie detail pages found: {len(all_movie_pages)}")

    found_links = []
    for url in all_movie_pages:
        print(f"🔎 Visiting movie: {url}")
        link = extract_gofile_link(url)
        if link:
            found_links.append(link)

    print(f"✅ Found {len(found_links)} GoFile links.")
    for i, link in enumerate(found_links, 1):
        ok = refresh_link(link)
        print(f"{i}. {link} → {'✅ Refreshed' if ok else '❌ Failed'}")


if __name__ == "__main__":
    run_refresh_job()
