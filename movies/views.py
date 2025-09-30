from django.shortcuts import render, get_object_or_404, redirect
from .models import Playlist, Movie, DownloadLog, InstallTracker, Category
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.http import require_POST
from django.utils import timezone
# Removed: send_mail, settings, messages (since contact_view and test_email are removed)
from django.db.models import Count, Q
from itertools import chain
import json
import re
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User


# -------------------------------
# Helper function: Episode and Season number (UPDATED)
# -------------------------------
def extract_episode_number(title):
    """
    Extracts the Season and Episode numbers from a movie/series title for correct sorting.
    Returns (season_num, episode_num).
    """
    # 1. Season extraction (e.g., Season-1 or S01)
    season_match = re.search(r"[Ss]eason\s*(\d+)|[Ss](\d+)", title)
    season_num = int(season_match.group(1) or season_match.group(2)) if season_match else 1 # Default to Season 1

    # 2. Episode extraction (e.g., Episode-10 or E10)
    episode_match = re.search(r"[Ee]pisode\s*(\d+)|[Ee](\d+)", title)
    
    if episode_match:
        episode_num = int(episode_match.group(1) or episode_match.group(2))
    else:
        # Fallback if only one number is present and it is likely the episode (e.g., just "12")
        # For movies with no explicit numbering, use a very high number to keep them last.
        episode_num = float("inf")
    
    # Returns (1, 10) for S1 E10, (2, 1) for S2 E1, etc.
    return (season_num, episode_num)


# ----------------------------------------------------------------------
# HOME VIEW (NO CHANGES NEEDED HERE, USING PREVIOUSLY FIXED LOGIC)
# ----------------------------------------------------------------------
def home(request):
    """Renders the homepage, including search functionality for movies and playlists."""
    query = request.GET.get("q")
    
    all_playlists = Playlist.objects.all()
    # Only show standalone movies (no playlist assigned) on home page
    all_movies = Movie.objects.filter(playlist__isnull=True) 

    if query:
        playlists_q = Q(name__icontains=query)
        movies_q = Q(title__icontains=query)
        
        all_playlists = all_playlists.filter(playlists_q)
        all_movies = all_movies.filter(movies_q) 
    
    combined_list = list(chain(all_playlists, all_movies))
    combined_list.sort(
        key=lambda x: x.created_at or timezone.datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )
    
    not_found = query and not combined_list
    
    return render(
        request,
        "home.html",
        {
            "media_items": combined_list,
            "categories": Category.objects.all(),
            "query": query,
            "not_found": not_found,
        },
    )


def playlist_detail(request, playlist_id):
    """
    Displays all movies belonging to a specific playlist.
    
    SORTING FIX: Movies are now sorted by Season number, then Episode number 
    using the title string for correct sequential ordering.
    """
    playlist = get_object_or_404(Playlist, id=playlist_id)
    
    # 1. Fetch all movies in the playlist
    movies = list(Movie.objects.filter(playlist=playlist))
    
    # 2. Sort them using the episode/season number extracted from the title
    # This ensures (S1, E1), (S1, E2), ..., (S1, E10), ..., (S2, E1) order.
    movies.sort(key=lambda movie: extract_episode_number(movie.title))
    
    return render(request, "playlist_detail.html", {"playlist": playlist, "movies": movies})


def category_detail(request, category_id):
    """Displays all playlists and movies belonging to a specific category, with search functionality."""
    category = get_object_or_404(Category, id=category_id)
    query = request.GET.get("q")
    movies = Movie.objects.filter(category=category)
    playlists = Playlist.objects.filter(category=category)

    if query:
        movies = movies.filter(title__icontains=query)
        playlists = playlists.filter(name__icontains=query)

    # Combine movies and playlists for display
    items = [{"type": "movie", "obj": m} for m in movies] + [{"type": "playlist", "obj": p} for p in playlists]
    items.sort(
        key=lambda x: x["obj"].created_at or timezone.datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )
    return render(request, "category_detail.html", {
        "category": category,
        "items": items,
        "query": query,
    })


def movie_detail(request, movie_id):
    """Displays the detail page for a specific movie."""
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, "movie_detail.html", {"movie": movie})


def get_client_ip(request):
    """Helper function to get the client's IP address."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def download_movie(request, movie_id):
    """
    Logs the download event and redirects the user to the actual download link.
    """
    movie = get_object_or_404(Movie, id=movie_id)
    ip = get_client_ip(request)
    agent = request.META.get("HTTP_USER_AGENT", "")
    user_email = request.user.email if request.user.is_authenticated else None
    username = request.user.username if request.user.is_authenticated else None

    # Create a log entry for the download
    DownloadLog.objects.create(
        movie_title=movie.title,
        ip_address=ip,
        user_agent=agent,
        user_email=user_email,
        username=username,
        download_time=timezone.now(),
    )
    # Redirect to the external download link
    return redirect(movie.download_link)


def detect_device_name(user_agent: str) -> str:
    """Tries to detect the device name from the User Agent string."""
    ua = user_agent.lower()
    if "windows" in ua:
        return "Windows PC/Laptop"
    elif "android" in ua:
        return "Android"
    elif "iphone" in ua or "ipad" in ua or "ios" in ua:
        return "iOS"
    elif "mac" in ua:
        return "Mac"
    else:
        return "Unknown"


@csrf_exempt
@require_POST
def track_install(request):
    """API endpoint to track PWA/App installation."""
    try:
        data = json.loads(request.body)
        device_id_str = data.get("device_id")
        device_name = data.get("device_name") or detect_device_name(request.META.get("HTTP_USER_AGENT", ""))

        if not device_id_str:
            return JsonResponse({"status": "error", "message": "Device ID missing"}, status=400)

        tracker, created = InstallTracker.objects.get_or_create(device_id=device_id_str)
        action_message = "Already tracked (count maintained)"

        if created:
            # First install
            tracker.install_count = 1
            tracker.deleted_count = 0
            tracker.device_info = request.META.get("HTTP_USER_AGENT", "")
            tracker.device_name = device_name
            tracker.last_action = "install"
            action_message = "New install tracked"
        elif tracker.install_count == 0:
            # Re-install after deletion
            tracker.install_count = 1
            tracker.device_name = device_name
            tracker.last_action = "reinstall"
            action_message = "Re-install tracked (count restored)"
        else:
            # Re-opening the app
            tracker.last_action = "install (re-open)"
            tracker.device_name = device_name

        tracker.updated_at = timezone.now()
        tracker.save()
        total_active_installs = InstallTracker.objects.filter(install_count=1).count()

        return JsonResponse({
            "status": "success",
            "message": action_message,
            "device": device_name,
            "total_active_installs": total_active_installs
        })

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
@require_POST
def track_uninstall(request):
    """API endpoint to track PWA/App uninstallation."""
    try:
        data = json.loads(request.body)
        device_id_str = data.get('device_id')

        if not device_id_str:
            return JsonResponse({'success': False, 'message': 'Device ID is required'}, status=400)

        try:
            tracker = InstallTracker.objects.get(device_id=device_id_str)
            if tracker.install_count == 1:
                tracker.install_count = 0
                tracker.deleted_count += 1
                tracker.last_action = 'uninstall'
                tracker.updated_at = timezone.now()
                tracker.save()

            total_active_installs = InstallTracker.objects.filter(install_count=1).count()

            return JsonResponse({'success': True, 'message': 'Uninstall tracked', 'total_active_installs': total_active_installs})
        except InstallTracker.DoesNotExist:
            return JsonResponse({'success': True, 'message': 'Tracker not found, but uninstall acknowledged'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Server error'}, status=500)


@staff_member_required
def custom_admin_dashboard(request):
    """Custom admin dashboard view showing key metrics."""
    total_users = User.objects.count()
    total_movies = Movie.objects.count()
    total_downloads = DownloadLog.objects.count()
    total_installs = InstallTracker.objects.filter(install_count=1).count()

    recent_installs = InstallTracker.objects.order_by('-updated_at')[:5]
    top_movies = DownloadLog.objects.values('movie_title').annotate(download_count=Count('movie_title')).order_by('-download_count')[:5]
    recent_downloads = DownloadLog.objects.order_by('-download_time')[:5]

    context = {
        'total_users': total_users,
        'total_movies': total_movies,
        'total_downloads': total_downloads,
        'total_installs': total_installs,
        'recent_installs': recent_installs,
        'top_movies': top_movies,
        'recent_downloads': recent_downloads,
    }
    return render(request, 'admin/index.html', context)


@staff_member_required
def reset_install_data(request):
    """Admin endpoint to clear all install tracking data."""
    InstallTracker.objects.all().delete()
    return JsonResponse({"status": "success", "message": "All install data has been reset."})
