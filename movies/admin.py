from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum # 👈 Yahan `Sum` import kiya hai
from .models import Playlist, Movie, DownloadLog, InstallTracker, Category

User = get_user_model()


# ---- Custom Admin Site ----
class MyAdminSite(admin.AdminSite):
    site_header = "Basharat Movies Hub Admin"
    site_title = "Basharat Admin"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        # ---- Top stats (Updated logic) ----
        # 📌 YEH LINE CHANGE KARO
        total_installs = InstallTracker.objects.aggregate(total=Sum('install_count'))['total'] or 0
        
        # 📌 YEH LINE CHANGE KARO
        total_uninstalls = InstallTracker.objects.aggregate(total=Sum('deleted_count'))['total'] or 0

        total_movies = Movie.objects.count()
        total_users = User.objects.count()
        total_downloads = DownloadLog.objects.count()

        # ---- Widgets data (Updated) ----
        recent_installs = InstallTracker.objects.order_by("-updated_at")[:5]

        top_movies = (
            DownloadLog.objects.values("movie_title")
            .annotate(download_count=Count("id"))
            .order_by("-download_count")[:5]
        )

        recent_downloads = DownloadLog.objects.order_by("-download_time")[:5]

        ctx = {
            "total_installs": total_installs,
            "total_uninstalls": total_uninstalls,
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
    list_display = ('title', 'category', 'playlist', 'poster_tag')
    search_fields = ('title',)
    list_filter = ('category', 'playlist',)

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


@admin.register(DownloadLog, site=admin_site)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ("movie_title", "username", "ip_address", "download_time")
    list_filter = ("download_time",)
    ordering = ("-download_time",)
    search_fields = ("movie_title", "username", "ip_address")


# 📦 InstallTracker model with updated admin
@admin.register(InstallTracker, site=admin_site)
class InstallTrackerAdmin(admin.ModelAdmin):
    list_display = ("device_id", "install_count", "deleted_count", "last_action", "updated_at", "created_at")
    list_filter = ("last_action", "updated_at", "created_at")
    ordering = ("-updated_at",)
    search_fields = ("device_id", "device_info")


# 📦 Category model admin
@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']