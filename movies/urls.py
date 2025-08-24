from django.urls import path
from .views import (
    home,
    playlist_detail,
    movie_detail,
    download_movie,
    track_install,
    track_uninstall,
    get_install_stats,
    contact_view,
    category_detail,  # नया view import किया
)

urlpatterns = [
    # Website pages
    path("", home, name="home"),
    path("playlist/<int:playlist_id>/", playlist_detail, name="playlist_detail"),
    path("category/<int:category_id>/", category_detail, name="category_detail"), # नया URL pattern जोड़ा
    path("movie/<int:movie_id>/", movie_detail, name="movie_detail"),
    path("download/<int:movie_id>/", download_movie, name="download_movie"),

    # Contact
    path("contact/", contact_view, name="contact"),

    # PWA Install & Uninstall Tracking
    path("track-install/", track_install, name="track_install"),
    path("track-uninstall/", track_uninstall, name="track_uninstall"),

    # AJAX endpoint
    path("ajax/install-stats/", get_install_stats, name="ajax_install_stats"),
]