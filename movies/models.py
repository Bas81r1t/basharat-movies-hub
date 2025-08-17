from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField  # ✅ Cloudinary import

class Playlist(models.Model):
    name = models.CharField(max_length=100)
    banner = CloudinaryField('banner', blank=True, null=True)  # ✅ Cloudinary banner field

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    poster = CloudinaryField('poster')  # ✅ Cloudinary poster field
    download_link = models.URLField()
    udrop_link = models.URLField(blank=True, null=True)  # ✅ 🔄 Auto Shuffle field added
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
        user_display = self.username or self.user_email or "Anonymous"
        return f"{self.movie_title} by {user_display} at {self.download_time.strftime('%Y-%m-%d %H:%M')}"

# ✅ New Model for PWA Install Tracking
class InstallTracker(models.Model):
    device_info = models.TextField()
    installed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_info[:30]}... ({self.installed_at.strftime('%Y-%m-%d %H:%M')})"
