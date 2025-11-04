from django.shortcuts import render, get_object_or_404, redirect
from .models import Playlist, Movie, DownloadLog, InstallTracker, Category
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count, Q
from itertools import chain
import json
import re
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage # EmptyPage को भी इम्पोर्ट किया


# -------------------------------
# Helper function: Robust Season and Episode number extraction
# -------------------------------
def extract_episode_number(title):
    """
    Extracts the Season and Episode numbers from a movie/series title for correct sorting.
    Returns (season_num, episode_num). This version is highly robust against bad titles.
    """
    title = title or ""
    title = title.lower()

    # Default values: Season 1, and a very high episode number (for movies or unsorted items)
    season_num = 1
    episode_num = 9999

    # 1. Season extraction (e.g., season 1, s01, s 1)
    # Searches for 's' or 'season' followed by digits
    season_match = re.search(r"s(?:eason)?\s*(\d+)", title)
    if season_match:
        try:
            # Safely convert to integer
            season_num = int(season_match.group(1))
        except ValueError:
            pass

    # 2. Episode extraction (e.g., episode 10, e10, e 10)
    # Searches for 'e' or 'episode' followed by digits
    episode_match = re.search(r"e(?:pisode)?\s*(\d+)", title)
    if episode_match:
        try:
            # Safely convert to integer
            episode_num = int(episode_match.group(1))
        except ValueError:
            pass

    # If no explicit episode found, check for a standalone number (which might be the episode number)
    # Only assign this if a season number was also found (to avoid treating movie years as episode numbers)
    if episode_num == 9999 and season_match:
        # Look for a standalone number that might represent the episode (e.g., "Series Title 12")
        # This part handles simple titles like "Show Name 1", "Show Name 2" within a season.
        cleaned_title = title.replace(season_match.group(0), '')
        simple_number_match = re.search(r"\b(\d+)\b", cleaned_title)
        if simple_number_match:
            try:
                # Safely convert to integer
                episode_num = int(simple_number_match.group(1))
            except ValueError:
                pass

    # Returns (1, 10) for S1 E10, (2, 1) for S2 E1, etc.
    return (season_num, episode_num)


# -------------------------------
# Helper function: Extracting order number (e.g., 1., 2., 10.)
# -------------------------------
def extract_movie_order_number(title):
    """
    Extracts the numeric order number (e.g., 1, 2, 10) from the start of a title.
    Returns 9999 if no number is found, ensuring it sorts last.
    """
    title = title or ""
    # RegEx searches for one or more digits at the start of the string, followed by a dot.
    match = re.match(r'^(\d+)\.', title.strip())
    if match:
        try:
            # Safely convert the captured number (group 1) to an integer
            return int(match.group(1))
        except ValueError:
            pass
    # Default to a high number if no sequence number is found
    return 9999


# ----------------------------------------------------------------------
# HOME VIEW (FIXED for 24/20 Pagination Overlap)
# ----------------------------------------------------------------------
def home(request):
    """Renders the homepage, including search functionality for movies and playlists."""
    query = request.GET.get("q")
    all_playlists = Playlist.objects.all()
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

    # --- 👇 FIXED Pagination Logic Yahan se Shuru Hota Hai! 👇 ---
    
    page_number = request.GET.get('page')
    
    # 1. Base Paginator Hamesha Page 1 ke Size (24) par set karo
    # Taki total pages ki calculation sahi ho.
    paginator = Paginator(combined_list, 24) 

    # 2. Requested page ka data fetch karo
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    except:
        page_obj = paginator.get_page(1) # Default to page 1 in case of any error


    # 3. Agar page 2 ya usse aage hain, toh Page 1 ke 'extra' 4 items ko hata do.
    # Page 1 = 24 items. Page 2, 3... = 20 items.
    
    # Check if we are not on the first page and there are enough items for slicing
    if page_obj.number > 1 and len(page_obj) > 4:
        # Paginator ne 24 items diye, hamein pehle ke 4 items hataane hain
        # Taki sirf 20 items bachein (24 - 4 = 20)
        # Slicing: [4:] ka matlab hai ki index 4 se aage ke saare items lo.
        media_items_sliced = page_obj.object_list[4:]
    elif page_obj.number == 1 or page_obj.number == paginator.num_pages:
        # First page ya last page par poore items dikhao (24 ya bache hue)
        media_items_sliced = page_obj.object_list
    else:
        # Default fallback
        media_items_sliced = page_obj.object_list

    # --- 👆 FIXED Pagination Logic Yahan Khatam Hota Hai! 👆 ---

    not_found = query and not combined_list
    return render(
        request,
        "home.html",
        {
            # Updated: media_items ko sliced list se set kar rahe hain, lekin page_obj original rahega
            "media_items": media_items_sliced, 
            "categories": Category.objects.all(),
            "query": query,
            "not_found": not_found,
            "page_obj": page_obj, # Pagination buttons is original page_obj ka use karenge
        },
    )


def playlist_detail(request, playlist_id):
    """
    Displays all movies belonging to a specific playlist.
    """
    playlist = get_object_or_404(Playlist, id=playlist_id)

    # 1. Fetch all movies in the playlist
    movies = list(Movie.objects.filter(playlist=playlist))

    # Check if this is a 'Movie Order' type playlist (like Marvel Universe)
    has_numeric_order = False

    # Check the first 5 movies (or fewer if the list is smaller)
    for movie in movies[:5]:
        if extract_movie_order_number(movie.title) != 9999:
            has_numeric_order = True
            break

    if has_numeric_order:
        # Sort using the numeric order from the title (1, 2, 3...)
        movies.sort(key=lambda movie: extract_movie_order_number(movie.title))

    else:
        # Default to Season/Episode sorting (S01E01, S01E02)
        movies.sort(key=lambda movie: extract_episode_number(movie.title))

    return render(request, "playlist_detail.html", {"playlist": playlist, "movies": movies})


def category_detail(request, category_id):
    """
    Displays all playlists and movies belonging to a specific category, with search functionality.
    Includes FIX for 24/20 Pagination Overlap.
    """
    category = get_object_or_404(Category, id=category_id)
    query = request.GET.get("q")

    # Category ke saare movies fetch kiye
    movies = list(Movie.objects.filter(category=category))
    playlists = Playlist.objects.filter(category=category)

    if query:
        movies = [m for m in movies if query.lower() in m.title.lower()] # Filtering movies in memory
        playlists = playlists.filter(name__icontains=query)

    # ------------------ SORTING LOGIC ------------------

    has_numeric_order = False
    for movie in movies[:5]:
        if extract_movie_order_number(movie.title) != 9999:
            has_numeric_order = True
            break

    if has_numeric_order:
        movies.sort(key=lambda movie: extract_movie_order_number(movie.title))

    items = [{"type": "movie", "obj": m} for m in movies] + [{"type": "playlist", "obj": p} for p in playlists]

    if not has_numeric_order:
        items.sort(
            key=lambda x: x["obj"].created_at or timezone.datetime.min.replace(tzinfo=timezone.utc),
            reverse=True
        )

    # --- 👇 FIXED Pagination Logic Yahan se Shuru Hota Hai! 👇 ---
    
    page_number = request.GET.get('page')

    # 1. Base Paginator Hamesha Page 1 ke Size (24) par set karo
    paginator = Paginator(items, 24) 
    
    # 2. Requested page ka data fetch karo
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    except:
        page_obj = paginator.get_page(1)
        

    # 3. Agar page 2 ya usse aage hain, toh Page 1 ke 'extra' 4 items ko hata do.
    # Logic: Page 1 = 24 items. Page 2, 3... = 20 items.
    
    if page_obj.number > 1 and len(page_obj.object_list) > 4:
        # Paginator ne 24 items diye, hamein pehle ke 4 items hataane hain
        media_items_sliced = page_obj.object_list[4:]
    elif page_obj.number == 1 or page_obj.number == paginator.num_pages:
        # First page ya last page par poore items dikhao (24 ya bache hue)
        media_items_sliced = page_obj.object_list
    else:
        # Default fallback
        media_items_sliced = page_obj.object_list
        
    # --- 👆 FIXED Pagination Logic Yahan Khatam Hota Hai! 👆 ---

    return render(request, "category_detail.html", {
        "category": category,
        # Updated: 'items' ab sliced list hai
        "items": media_items_sliced, 
        "query": query,
        "page_obj": page_obj, # Pagination buttons is original page_obj ka use karenge
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

    DownloadLog.objects.create(
        movie_title=movie.title,
        ip_address=ip,
        user_agent=agent,
        user_email=user_email,
        username=username,
        download_time=timezone.now(),
    )
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
            tracker.install_count = 1
            tracker.deleted_count = 0
            tracker.device_info = request.META.get("HTTP_USER_AGENT", "")
            tracker.device_name = device_name
            tracker.last_action = "install"
            action_message = "New install tracked"
        elif tracker.install_count == 0:
            tracker.install_count = 1
            tracker.device_name = device_name
            tracker.last_action = "reinstall"
            action_message = "Re-install tracked (count restored)"
        else:
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