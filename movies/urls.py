from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import admin


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
    # PWA Install & Uninstall Tracking
    # -------------------------
    path("track-install/", views.track_install, name="track_install"),
    path("track-uninstall/", views.track_uninstall, name="track_uninstall"),

    # -------------------------
    # Authentication Views
    # -------------------------
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),

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
