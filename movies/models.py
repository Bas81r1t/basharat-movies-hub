from django.db import models
from django.utils import timezone

class Playlist(models.Model):
    name = models.CharField(max_length=100)
    banner = models.ImageField(upload_to='playlist_banners/', blank=True, null=True)
    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    poster = models.ImageField(upload_to='posters/')
    download_link = models.URLField()
    playlist = models.ForeignKey(Playlist, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class DownloadLog(models.Model):
    movie_title = models.CharField(max_length=200)
    download_time = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    user_email = models.EmailField(blank=True, null=True)
    username = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.movie_title} by {self.username or 'Anonymous'}"