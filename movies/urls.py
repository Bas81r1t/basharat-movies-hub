from django.urls import path
from .views import (
    home, playlist_detail, movie_detail, download_movie, track_install
)

urlpatterns = [
    path('', home, name='home'),
    path('playlist/<int:playlist_id>/', playlist_detail, name='playlist_detail'),
    path('movie/<int:movie_id>/', movie_detail, name='movie_detail'),
    path('download/<int:movie_id>/', download_movie, name='download_movie'),

    # ✅ PWA install tracking
    path('track-install/', track_install, name='track_install'),
]
