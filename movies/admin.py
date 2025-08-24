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
        # ✅ Updated queries to use the new models
        total_installs = InstallTracker.objects.filter(last_action='install').aggregate(total_installs=Count('device_id'))['total_installs'] or 0
        total_deletes = InstallTracker.objects.filter(last_action='uninstall').aggregate(total_deletes=Count('device_id'))['total_deletes'] or 0
        total_movies = Movie.objects.count()
        total_users = User.objects.count()
        total_downloads = DownloadLog.objects.count()

        # ---- Widgets data ----
        # ✅ Updated queries for recent installs
        recent_installs = (
            InstallTracker.objects.filter(last_action='install')
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
    list_display = ('title', 'playlist', 'poster_tag')
    search_fields = ('title',)
    list_filter = ('playlist',)

    def poster_tag(self, obj):
        if obj.poster:
            from django.utils.html import format_html
            return format_html('<img src="{}" width="50" height="50" />', obj.poster.url)
        return 'No Poster'

    poster_tag.short_description = 'Poster'
    poster_tag.allow_tags = True


@admin.register(Playlist, site=admin_site)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name',)
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
        "device_id",
        "install_count",
        "deleted_count",
        "last_action",
        "updated_at",
        "created_at",
    )
    list_filter = ("last_action", "updated_at", "created_at")
    ordering = ("-updated_at",)
    search_fields = ("device_id",)