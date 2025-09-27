from django.shortcuts import render, get_object_or_404, redirect
from .models import Playlist, Movie, DownloadLog, InstallTracker, Category
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q
from itertools import chain
import json
import re
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User


# ----------------------------------------------------------------------
# 🎬 UPDATED MOVIE REQUEST VIEW
# ----------------------------------------------------------------------
@csrf_exempt
def movie_request(request):
    if request.method == "POST":
        movie_name = request.POST.get("movie_name", "").strip()
        user_email = request.POST.get("user_email", "").strip()

        if not movie_name:
            return JsonResponse({"status": "error", "message": "Movie name required"}, status=400)

        subject = f"🎬 NEW MOVIE REQUEST: {movie_name}"
        body = f"User is requesting: {movie_name}\nContact Email: {user_email or 'Not provided'}"

        try:
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False
            )
            return JsonResponse({"status": "success", "message": "Request sent successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)


# ----------------------------------------------------------------------
# ⚙️ EXISTING VIEWS 
# ----------------------------------------------------------------------

def extract_episode_number(title):
    match = re.search(r"[Ee]pisode\s*(\d+)", title)
    if match:
        return int(match.group(1))
    match = re.search(r"\d+", title)
    if match:
        return int(match.group())
    return float("inf")


def home(request):
    query = request.GET.get("q")
    all_playlists = Playlist.objects.all()
    all_movies = Movie.objects.all()

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
    playlist = get_object_or_404(Playlist, id=playlist_id)
    movies = Movie.objects.filter(playlist=playlist).order_by('-created_at')
    return render(request, "playlist_detail.html", {"playlist": playlist, "movies": movies})


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    query = request.GET.get("q")
    movies = Movie.objects.filter(category=category)
    playlists = Playlist.objects.filter(category=category)

    if query:
        movies = movies.filter(title__icontains=query)
        playlists = playlists.filter(name__icontains=query)

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
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, "movie_detail.html", {"movie": movie})


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def download_movie(request, movie_id):
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
    if request.method == 'POST':
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

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


@staff_member_required
def custom_admin_dashboard(request):
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
    InstallTracker.objects.all().delete()
    return JsonResponse({"status": "success", "message": "All install data has been reset."})


def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not message:
            messages.error(request, "❌ All fields are required.")
            return redirect("contact")

        subject = f"📩 New Contact Form Message from {name}"
        body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"

        try:
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False
            )
            messages.success(request, "✅ Message sent successfully! We’ll contact you soon.")
        except Exception as e:
            messages.error(request, "❌ Could not send message. Please try again later.")
            print(f"Contact form email error: {e}")

        return redirect("contact")

    return render(request, "contact.html")
