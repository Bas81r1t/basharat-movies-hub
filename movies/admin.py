from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count
from .models import Playlist, Movie, DownloadLog, InstallTracker

User = get_user_model()


class MyAdminSite(admin.AdminSite):
    site_header = "Basharat Movies Hub Admin"
    site_title = "Basharat Admin"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        # ---- Top stats ----
        total_installs = InstallTracker.objects.count()
        total_movies = Movie.objects.count()
        total_users = User.objects.count()
        total_downloads = DownloadLog.objects.count()

        # ---- Widgets data ----
        recent_installs = InstallTracker.objects.order_by("-installed_at")[:5]

        top_movies = (
            DownloadLog.objects.values("movie_title")
            .annotate(download_count=Count("id"))
            .order_by("-download_count")[:5]
        )

        recent_downloads = DownloadLog.objects.order_by("-download_time")[:5]

        ctx = {
            "total_installs": total_installs,
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


# ---- Create custom admin site instance ----
admin_site = MyAdminSite(name="myadmin")


# ---- ModelAdmin classes (optional display tweaks) ----
class MovieAdmin(admin.ModelAdmin):
    exclude = ("udrop_link",)


class PlaylistAdmin(admin.ModelAdmin):
    pass


class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ("movie_title", "username", "ip_address", "download_time")
    list_filter = ("download_time",)
    ordering = ("-download_time",)
    search_fields = ("movie_title", "username", "ip_address")


class InstallTrackerAdmin(admin.ModelAdmin):
    list_display = ("device_info", "installed_at")
    list_filter = ("installed_at",)
    ordering = ("-installed_at",)
    search_fields = ("device_info",)


# ❗ IMPORTANT: register with *custom* site, not default admin.site
admin_site.register(Movie, MovieAdmin)
admin_site.register(Playlist, PlaylistAdmin)
admin_site.register(DownloadLog, DownloadLogAdmin)
admin_site.register(InstallTracker, InstallTrackerAdmin)
