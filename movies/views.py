from django.shortcuts import render, get_object_or_404, redirect
from django.http import StreamingHttpResponse, HttpResponseBadRequest
from .models import Playlist, Movie, DownloadLog
import requests

# ---------------- HOME & MOVIE VIEWS ----------------
def home(request):
    query = request.GET.get('q')
    playlists = Playlist.objects.all()
    movies = None
    not_found = False
    unlisted_movies = Movie.objects.filter(playlist__isnull=True)  # 🎯 Movies without playlist

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


# ---------------- DOWNLOAD LOGGING ----------------
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def download_movie(request, movie_id):
    """
    Old redirect replaced with proxy stream to bypass IP block.
    """
    movie = get_object_or_404(Movie, id=movie_id)

    # Log the download attempt
    ip = get_client_ip(request)
    agent = request.META.get('HTTP_USER_AGENT', '')
    user_email = request.user.email if request.user.is_authenticated else None
    username = request.user.username if request.user.is_authenticated else None

    DownloadLog.objects.create(
        movie_title=movie.title,
        ip_address=ip,
        user_agent=agent,
        user_email=user_email,
        username=username
    )

    # Call proxy to stream file
    return proxy_gofile(request, movie.download_link)


# ---------------- GOFILE PROXY ----------------
def proxy_gofile(request, gofile_url=None):
    """
    Streams file from GoFile server-side to bypass region/IP block.
    """
    if not gofile_url:
        gofile_url = request.GET.get("url")
        if not gofile_url:
            return HttpResponseBadRequest("Missing 'url' parameter")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(gofile_url, headers=headers, stream=True, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        return HttpResponseBadRequest(f"Error fetching file: {e}")

    content_type = r.headers.get("Content-Type", "application/octet-stream")
    response = StreamingHttpResponse(r.iter_content(chunk_size=8192), content_type=content_type)

    # Preserve filename if available
    if "Content-Disposition" in r.headers:
        response['Content-Disposition'] = r.headers['Content-Disposition']
    else:
        response['Content-Disposition'] = "inline"

    return response
