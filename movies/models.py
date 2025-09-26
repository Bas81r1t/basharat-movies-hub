from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField

# 🔹 Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# 🔹 Playlist Model
class Playlist(models.Model):
    name = models.CharField(max_length=100)
    banner = CloudinaryField("banner", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# 🔹 Movie Model
class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    poster = CloudinaryField("poster")
    download_link = models.URLField()
    udrop_link = models.URLField(blank=True, null=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title


# 🔹 Download Log Model
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


# 🔹 Install Tracker Model (Unique Installs Only)
class InstallTracker(models.Model):
    device_id = models.CharField(max_length=255, unique=True)  # unique device
    device_name = models.CharField(max_length=100, blank=True, null=True)  # Android / iOS / Windows PC/Laptop
    install_count = models.PositiveIntegerField(default=1)  # Always 1 for unique installs
    last_action = models.CharField(max_length=20, default="Install")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_id} ({self.device_name or 'Unknown'})"
