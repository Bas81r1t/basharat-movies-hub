from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count
from .models import Playlist, Movie, DownloadLog, InstallTracker

User = get_user_model()


# ---- Custom Admin Site ----
class MyAdminSite(admin.AdminSite):
    site_header = "Basharat Movies Hub Admin"
    site_title = "Basharat Admin"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        # ---- Top stats (CURRENT state) ----
        total_installs = InstallTracker.objects.filter(installed=True).count()   # ✅ currently installed devices
        total_deletes = InstallTracker.objects.filter(installed=False).count()  # ✅ currently uninstalled devices
        total_movies = Movie.objects.count()
        total_users = User.objects.count()
        total_downloads = DownloadLog.objects.count()

        # ---- Widgets data ----
        recent_installs = (
            InstallTracker.objects.filter(installed=True)
            .order_by("-updated_at")[:5]
        )

        top_movies = (
            DownloadLog.objects.values("movie_title")
            .annotate(download_count=Count("id"))
            .order_by("-download_count")[:5]
        )

        recent_downloads = DownloadLog.objects.order_by("-download_time")[:5]

        ctx = {
            "total_installs": total_installs,
            "total_deletes": total_deletes,
            "total_movies": total_movies,
            "total_users": total_users,
            "total_downloads": total_downloads,
            "recent_installs": recent_installs,
            "top_movies": top_movies,
            "recent_downloads": recent_downloads,
        }
        if extra_context:
            ctx.update(extra_context)
        return super().index(request, extra_context=ctx)


# ---- Custom admin site instance ----
admin_site = MyAdminSite(name="myadmin")


# ---- ModelAdmin classes ----
@admin.register(Movie, site=admin_site)
class MovieAdmin(admin.ModelAdmin):
    exclude = ("udrop_link",)


@admin.register(Playlist, site=admin_site)
class PlaylistAdmin(admin.ModelAdmin):
    pass


@admin.register(DownloadLog, site=admin_site)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ("movie_title", "username", "ip_address", "download_time")
    list_filter = ("download_time",)
    ordering = ("-download_time",)
    search_fields = ("movie_title", "username", "ip_address")


@admin.register(InstallTracker, site=admin_site)
class InstallTrackerAdmin(admin.ModelAdmin):
    list_display = (
        "device_info",
        "installed",        # ✅ current state (True/False)
        "install_count",    # ✅ cumulative installs
        "delete_count",     # ✅ cumulative deletes
        "last_action",
        "updated_at",
        "created_at",
    )
    list_filter = ("installed", "last_action", "updated_at", "created_at")
    ordering = ("-updated_at",)
    search_fields = ("device_info",)
