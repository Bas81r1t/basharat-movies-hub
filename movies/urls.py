from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    # -------------------------
    # Website Pages
    # -------------------------
    path("", views.home, name="home"),
    path("playlist/<int:playlist_id>/", views.playlist_detail, name="playlist_detail"),
    path("category/<int:category_id>/", views.category_detail, name="category_detail"),
    path("movie/<int:movie_id>/", views.movie_detail, name="movie_detail"),
    path("download/<int:movie_id>/", views.download_movie, name="download_movie"),

    # -------------------------
    # Contact Form
    # -------------------------
    path("contact/", views.contact_view, name="contact"),

    # -------------------------
    # PWA Install & Uninstall Tracking
    # -------------------------
    path("track-install/", views.track_install, name="track_install"),
    path("track-uninstall/", views.track_uninstall, name="track_uninstall"),

    # -------------------------
    # Admin Dashboard URLs
    # -------------------------
    path("admin/dashboard/", views.custom_admin_dashboard, name="admin_dashboard"),
    path("admin/reset-install-data/", views.reset_install_data, name="reset_install_data"),

    # -------------------------
    # Django Admin
    # -------------------------
    path("admin/", admin.site.urls),
]
