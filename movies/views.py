from django.shortcuts import render, get_object_or_404, redirect
from .models import Playlist, Movie, DownloadLog, InstallTracker
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.utils import timezone
import json

# ------------------------
# Existing Views
# ------------------------
def home(request):
    query = request.GET.get('q')
    playlists = Playlist.objects.all()
    movies = None
    not_found = False
    unlisted_movies = Movie.objects.filter(playlist__isnull=True)

    if query:
        movies = Movie.objects.filter(title__icontains=query)
        if not movies.exists():
            not_found = True

    return render(request, 'home.html', {
        'playlists': playlists,
        'movies': movies,
        'query': query,
        'not_found': not_found,
        'unlisted_movies': unlisted_movies
    })

def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    movies = Movie.objects.filter(playlist=playlist)
    return render(request, 'playlist_detail.html', {
        'playlist': playlist,
        'movies': movies
    })

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movie_detail.html', {'movie': movie})

# ------------------------
# Helper to get client IP
# ------------------------
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

# ------------------------
# Download Logging
# ------------------------
def download_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    ip = get_client_ip(request)
    agent = request.META.get('HTTP_USER_AGENT', '')
    user_email = request.user.email if request.user.is_authenticated else None
    username = request.user.username if request.user.is_authenticated else None

    # ✅ Save download log (TypeError fix)
    DownloadLog.objects.create(
        movie_title=movie.title,   # sirf ye rakho
        ip_address=ip,
        user_agent=agent,
        user_email=user_email,
        username=username,
        download_time=timezone.now()
    )

    # ✅ Redirect to actual download link
    return redirect(movie.download_link)

# ------------------------
# PWA Install Tracking
# ------------------------
@csrf_exempt
def track_install(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            device = data.get('device', 'Unknown device')
            InstallTracker.objects.create(device_info=device)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'fail'})

# ------------------------
# AJAX endpoint for live stats
# ------------------------
@require_GET
def get_install_stats(request):
    total_installs = InstallTracker.objects.count()
    recent_installs = list(
        InstallTracker.objects.order_by('-installed_at')[:5]
        .values('device_info', 'installed_at')
    )
    for r in recent_installs:
        r['installed_at'] = r['installed_at'].strftime('%d %b %Y %H:%M')

    return JsonResponse({
        'total_installs': total_installs,
        'recent_installs': recent_installs
    })
