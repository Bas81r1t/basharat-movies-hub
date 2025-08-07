import requests
from bs4 import BeautifulSoup

BASE_URL = "https://basharat-movies-hub.onrender.com"

# Step 1: Get all playlist pages
def get_playlist_urls():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    playlist_links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        if "/playlist/" in href:
            if href.startswith("http"):
                playlist_links.append(href)
            else:
                playlist_links.append(BASE_URL + href)
    return playlist_links

# Step 2: Get movie links from each playlist
def get_movie_links_from_playlists(playlist_urls):
    movie_links = []
    for url in playlist_urls:
        try:
            res = requests.get(url)
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
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "gofile.io/d/" in href:
                    print(f"🎯 Found GoFile link: {href}")
                    gofile_links.append(href)
        except Exception as e:
            print(f"❌ Error fetching movie page {url}: {e}")
    return gofile_links

# Step 4: Refresh each GoFile link
def refresh_links():
    playlist_urls = get_playlist_urls()
    print(f"📁 Total playlists found: {len(playlist_urls)}")

    movie_urls = get_movie_links_from_playlists(playlist_urls)
    print(f"🎬 Total movies found: {len(movie_urls)}")

    gofile_links = extract_gofile_links_from_movie_pages(movie_urls)
    print(f"🔗 Total GoFile links found: {len(gofile_links)}")

    for link in gofile_links:
        try:
            r = requests.get(link)
            print(f"✅ Refreshed: {link} | Status: {r.status_code}")
        except Exception as e:
            print(f"❌ Error refreshing {link}: {e}")

if __name__ == "__main__":
    refresh_links()
