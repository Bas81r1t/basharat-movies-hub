from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('playlist/<int:movie_id>/', views.movie_detail, name='movie_detail_legacy'),  # optional safety; keep old patterns if needed
    path('playlist/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('download/<int:movie_id>/', views.download_movie, name='download_movie'),
]
