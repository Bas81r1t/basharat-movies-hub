from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse, HttpResponseBadRequest, FileResponse
from django.conf import settings
from .models import Playlist, Movie, DownloadLog
import os
import requests
from requests.adapters import HTTPAdapter, Retry

# ============== CONFIG ==============
# .env / settings.py me set karo:
# PROXY_URLS = "http://user:pass@us-proxy:port, http://user:pass@eu-proxy:port"
# (Agar auth nahi hai to: "http://us-proxy:port")
PROXY_URLS = []
_raw = getattr(settings, "PROXY_URLS", "")
if _raw:
    PROXY_URLS = [u.strip() for u in _raw.split(",") if u.strip()]

# OPTIONAL local cache (agar chaho)
CACHE_DIR = os.path.join(getattr(settings, "BASE_DIR", os.getcwd()), "cache_movies")
os.makedirs(CACHE_DIR, exist_ok=True)

# ============== HELPERS ==============
def _session_with_retries():
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=["GET", "HEAD"]
    )
    adapter = HTTPAdapter(max_retries=retries, pool_maxsize=10, pool_connections=10)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    return s

def _fetch_stream(url, use_cache=False, filename_hint=None):
    """
    Try proxies in order; if none work, try direct as last resort.
    Returns: (response_like, is_file_response)
    """
    # 1) CACHE (optional)
    if use_cache:
        safe_name = (filename_hint or "file").replace("/", "_").replace("\\", "_")
        local_path = os.path.join(CACHE_DIR, safe_name)
        if os.path.exists(local_path):
            # Serve from local
            return FileResponse(open(local_path, "rb"), as_attachment=False), True

    # 2) Try via proxies
    sess = _session_with_retries()
    targets = (PROXY_URLS + ["DIRECT"]) if PROXY_URLS else ["DIRECT"]

    last_exc = None
    for proxy in targets:
        try:
            if proxy == "DIRECT":
                proxies = None
            else:
                proxies = {"http": proxy, "https": proxy}

            r = sess.get(url, proxies=proxies, stream=True, timeout=20)
            r.raise_for_status()

            # If caching requested, store while streaming to user’s response
            if use_cache:
                # Write to temp then rename (safer)
                tmp_path = local_path + ".part"
                with open(tmp_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                os.replace(tmp_path, local_path)
                return FileResponse(open(local_path, "rb"), as_attachment=False), True

            # No cache: just stream
            content_type = r.headers.get("Content-Type", "application/octet-stream")
            resp = StreamingHttpResponse(r.iter_content(chunk_size=8192), content_type=content_type)
            disp = r.headers.get("Content-Disposition", "inline")
            resp["Content-Disposition"] = disp
            return resp, False

        except Exception as e:
            last_exc = e
            continue

    raise requests.RequestException(last_exc or "All proxy attempts failed")

# ============== YOUR EXISTING VIEWS ==============
from django.db.models import Q

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

# ============== DOWNLOAD LOG + PROXY STREAM ==============
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def download_movie(request, movie_id):
    """
    User clicks download/play:
    - Log the attempt
    - Stream via proxy/VPN-exit if configured
    - If PROXY_URLS empty, will try DIRECT as fallback
    """
    movie = get_object_or_404(Movie, id=movie_id)

    # Log
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

    # Stream via proxy (no cache; for cache change to True and set filename)
    try:
        # filename hint for cache (optional): f"{movie.id}_{movie.title}.mp4"
        resp, is_file = _fetch_stream(movie.download_link, use_cache=False, filename_hint=None)
        return resp
    except requests.RequestException as e:
        return HttpResponseBadRequest(f"Fetch failed: {e}")
from django.shortcuts import render, get_object_or_404
from .models import Playlist, Movie

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
        'unlisted_movies': unlisted_movies  # Pass to template
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

from django.shortcuts import redirect, get_object_or_404
from .models import Movie, DownloadLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def download_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

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

    return redirect(movie.download_link)

