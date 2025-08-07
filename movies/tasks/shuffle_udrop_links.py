import sys
import os
import django
import requests
import random

# ✅ Add this to fix module import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basharat.settings')
django.setup()

from movies.models import Movie

# Dummy example – future me tum apne udrop API ya source se link fetch karoge
sample_links = [
    'https://udrop.link/abc123',
    'https://udrop.link/xyz456',
    'https://udrop.link/pqr789',
]

def update_links():
    for movie in Movie.objects.all():
        new_link = random.choice(sample_links)
        movie.udrop_link = new_link
        movie.save()
        print(f"✅ Updated: {movie.title} ➜ {new_link}")

if __name__ == "__main__":
    update_links()
