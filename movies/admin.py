from django.contrib import admin
from .models import Playlist, Movie, DownloadLog, InstallTracker

# Movie Admin
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    exclude = ('udrop_link',)  # ✅ Hide udrop_link from admin panel

# Playlist Admin
@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    pass

# DownloadLog Admin
@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user_ip', 'downloaded_at')
    list_filter = ('downloaded_at',)

# InstallTracker Admin
@admin.register(InstallTracker)
class InstallTrackerAdmin(admin.ModelAdmin):
    list_display = ('device_info', 'installed_at')  # ✅ Dekhne ke liye columns
    list_filter = ('installed_at',)                 # Filter by date
    ordering = ('-installed_at',)                  # Latest install top
