from django.contrib import admin
from .models import Playlist, Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    exclude = ('udrop_link',)  # ✅ Hide udrop_link from admin panel

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    pass
