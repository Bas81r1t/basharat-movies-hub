import os
import django
import requests
import time

# Django settings load karo
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "basharat.settings")
django.setup()

from movies.models import Movie

def refresh_links():
    movies = Movie.objects.all()
    for movie in movies:
        link = movie.download_link
        if link:
            print(f"Refreshing: {link}")
            try:
                response = requests.get(link)
                if response.status_code == 200:
                    print("✅ Refreshed")
                else:
                    print(f"❌ Error: {response.status_code}")
            except Exception as e:
                print(f"❌ Exception: {e}")
            time.sleep(5)

if __name__ == "__main__":
    refresh_links()
