from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Movie, Playlist
import cloudinary.uploader

@receiver(post_delete, sender=Movie)
def delete_movie_data(sender, instance, **kwargs):
    if instance.poster:
        public_id = instance.poster.public_id  # ✅ Correct way for CloudinaryField
        cloudinary.uploader.destroy(public_id)

@receiver(post_delete, sender=Playlist)
def delete_playlist_data(sender, instance, **kwargs):
    if instance.banner:
        public_id = instance.banner.public_id  # ✅ Correct way for CloudinaryField
        cloudinary.uploader.destroy(public_id)
