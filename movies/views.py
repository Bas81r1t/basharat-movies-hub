from django.shortcuts import render, get_object_or_404, redirect
from .models import Playlist, Movie, DownloadLog, InstallTracker, Category
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import json
import re
import uuid


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
    playlists = Playlist.objects.all()
    categories = Category.objects.all()
    movies = None
    not_found = False
    unlisted_movies = Movie.objects.filter(playlist__isnull=True)

    if query:
        movies = Movie.objects.filter(title__icontains=query)
        if not movies.exists():
            not_found = True

    return render(
        request,
        "home.html",
        {
            "playlists": playlists,
            "categories": categories,
            "movies": movies,
            "query": query,
            "not_found": not_found,
            "unlisted_movies": unlisted_movies,
        },
    )


def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    movies = Movie.objects.filter(playlist=playlist)
    movies = sorted(movies, key=lambda m: extract_episode_number(m.title))
    return render(request, "playlist_detail.html", {"playlist": playlist, "movies": movies})


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    # Movies and Playlists under this category
    movies = list(Movie.objects.filter(category=category))
    playlists = list(Playlist.objects.filter(category=category))

    # Merge both into one list (with type info)
    items = []
    for m in movies:
        items.append({"type": "movie", "obj": m})
    for p in playlists:
        items.append({"type": "playlist", "obj": p})

    return render(request, "category_detail.html", {
        "category": category,
        "items": items
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


@csrf_exempt
@require_POST
def track_install(request):
    try:
        data = json.loads(request.body or "{}")
        device_id_str = data.get("device_id")
        device_info = data.get("device_info") or ""

        if device_id_str:
            device_id = uuid.UUID(device_id_str)
        else:
            device_id = uuid.uuid4()

        tracker, created = InstallTracker.objects.get_or_create(device_id=device_id)

        if created:
            tracker.install_count = 1
        elif tracker.last_action == "uninstall":
            tracker.install_count += 1
            tracker.deleted_count = max(0, tracker.deleted_count - 1)

        if device_info:
            tracker.device_info = device_info[:255]

        tracker.last_action = "install"
        tracker.save()

        return JsonResponse({"status": "success", "device_id": str(device_id)})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@csrf_exempt
@require_POST
def track_uninstall(request):
    try:
        data = json.loads(request.body or "{}")
        device_id_str = data.get("device_id")
        if not device_id_str:
            return JsonResponse({"status": "error", "message": "Device ID missing"}, status=400)

        device_id = uuid.UUID(device_id_str)

        try:
            tracker = InstallTracker.objects.get(device_id=device_id)
            if tracker.last_action == "install":
                tracker.deleted_count += 1
                tracker.install_count = max(0, tracker.install_count - 1)
                tracker.last_action = "uninstall"
                device_info = (data.get("device_info") or "")[:255]
                if device_info:
                    tracker.device_info = device_info
                tracker.save()
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "info", "message": "Already marked as uninstalled"})
        except InstallTracker.DoesNotExist:
            return JsonResponse({"status": "info", "message": "Device not found, no action taken"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@require_GET
def get_install_stats(request):
    total_installs = InstallTracker.objects.filter(last_action="install").count()
    total_deletes = InstallTracker.objects.filter(last_action="uninstall").count()
    return JsonResponse({"installs": total_installs, "deletes": total_deletes})


def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        subject = f"📩 New Contact Form Message from {name}"
        body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"

        try:
            send_mail(subject, body, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)
            messages.success(request, "✅ Message sent successfully! We’ll contact you soon.")
        except Exception as e:
            messages.error(request, "❌ Could not send message. Please try again later.")
            print(f"Contact form email error: {e}")

        return redirect("contact")

    return render(request, "contact.html")
