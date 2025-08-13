from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('playlist/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),

    # Download (now streams via proxy)
    path('download/<int:movie_id>/', views.download_movie, name='download_movie'),

    # Optional direct proxy access if you want to test
    path('proxy/', views.proxy_gofile, name='proxy_gofile'),
]
