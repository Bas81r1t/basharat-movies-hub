from django.contrib import admin
from .models import Playlist, Movie, DownloadLog, InstallTracker

# ----------------------
# Custom AdminSite
# ----------------------
class MyAdminSite(admin.AdminSite):
    site_header = "Basharat Movies Hub Admin"

    def index(self, request, extra_context=None):
        from .models import InstallTracker
        total_installs = InstallTracker.objects.count()
        recent_installs = InstallTracker.objects.order_by('-installed_at')[:5]

        extra_context = extra_context or {}
        extra_context['total_installs'] = total_installs
        extra_context['recent_installs'] = recent_installs
        return super().index(request, extra_context=extra_context)


# ----------------------
# Register AdminSite
# ----------------------
admin_site = MyAdminSite(name='myadmin')

# ----------------------
# Movie Admin
# ----------------------
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    exclude = ('udrop_link',)

# ----------------------
# Playlist Admin
# ----------------------
@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    pass

# ----------------------
# DownloadLog Admin
# ----------------------
@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ('movie_title', 'username', 'ip_address', 'download_time')
    list_filter = ('download_time',)
    ordering = ('-download_time',)
    search_fields = ('movie_title', 'username', 'ip_address')

# ----------------------
# InstallTracker Admin
# ----------------------
@admin.register(InstallTracker)
class InstallTrackerAdmin(admin.ModelAdmin):
    list_display = ('device_info', 'installed_at')
    list_filter = ('installed_at',)
    ordering = ('-installed_at',)
    search_fields = ('device_info',)
