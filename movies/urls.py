from django.urls import path
from .views import (
    home,
    playlist_detail,
    movie_detail,
    download_movie,
    track_install,
    get_install_stats,
    contact_view,  # ✅ Contact form
)

urlpatterns = [
    # ------------------------
    # Website pages
    # ------------------------
    path('', home, name='home'),
    path('playlist/<int:playlist_id>/', playlist_detail, name='playlist_detail'),
    path('movie/<int:movie_id>/', movie_detail, name='movie_detail'),
    path('download/<int:movie_id>/', download_movie, name='download_movie'),

    # ------------------------
    # Contact Form
    # ------------------------
    path('contact/', contact_view, name='contact'),

    # ------------------------
    # PWA Install Tracking
    # ------------------------
    path('track-install/', track_install, name='track_install'),

    # ------------------------
    # AJAX endpoint for live stats (Admin Dashboard / others)
    # ------------------------
    path('ajax/install-stats/', get_install_stats, name='ajax_install_stats'),
]
