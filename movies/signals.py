from django.contrib.admin.models import LogEntry
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Movie, Playlist

@receiver(post_delete, sender=Movie)
def delete_movie_logs(sender, instance, **kwargs):
    LogEntry.objects.filter(object_id=instance.id).delete()

@receiver(post_delete, sender=Playlist)
def delete_playlist_logs(sender, instance, **kwargs):
    LogEntry.objects.filter(object_id=instance.id).delete()
