from django.shortcuts import render, get_object_or_404, redirect
from .models import Playlist, Movie, DownloadLog, InstallTracker, Category
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib import messages
from django.db.models import Sum
import json
import re
import uuid

# 🔹 Helper function: Extract episode number
def extract_episode_number(title):
    match = re.search(r"[Ee]pisode\s*(\d+)", title)
    if match:
        return int(match.group(1))
    match = re.search(r"\d+", title)
    if match:
        return int(match.group())
    return float("inf")


# 🔹 Home Page
def home(request):
    query = request.GET.get("q")
    playlists = Playlist.objects.all()
    categories = Category.objects.all()
    movies = None
    not_found = False
    unlisted_movies = Movie.objects.filter(playlist__isnull=True)

    if query:
        playlists = Playlist.objects.filter(name__icontains=query)
        if not playlists.exists():
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


# 🔹 Playlist Detail
def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    movies = Movie.objects.filter(playlist=playlist)
    movies = sorted(movies, key=lambda m: extract_episode_number(m.title))
    return render(request, "playlist_detail.html", {"playlist": playlist, "movies": movies})


# 🔹 Category Detail
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    movies = list(Movie.objects.filter(category=category))
    playlists = list(Playlist.objects.filter(category=category))

    query = request.GET.get("q")
    if query:
        movies = [m for m in movies if query.lower() in m.title.lower()]
        playlists = [p for p in playlists if query.lower() in p.name.lower()]

    items = []
    for m in movies:
        items.append({"type": "movie", "obj": m})
    for p in playlists:
        items.append({"type": "playlist", "obj": p})

    items.sort(key=lambda x: (0 if x["type"] == "movie" else 1, str(x["obj"])))

    return render(request, "category_detail.html", {
        "category": category,
        "items": items,
        "query": query,
    })


# 🔹 Movie Detail
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, "movie_detail.html", {"movie": movie})


# 🔹 Get Client IP
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


# 🔹 Download Movie
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


# 🔹 Track Install
@csrf_exempt
@require_POST
def track_install(request):
    try:
        data = json.loads(request.body or "{}")
        device_id_str = data.get("device_id")
        device_info = (data.get("device_info") or "")[:255]

        if not device_id_str:
            return JsonResponse({"status": "error", "message": "Device ID missing"}, status=400)

        device_id = uuid.UUID(device_id_str)
        tracker, created = InstallTracker.objects.get_or_create(
            device_id=device_id,
            defaults={"device_info": device_info}
        )

        tracker.install_count = 1
        tracker.last_action = "install"
        tracker.device_info = device_info or tracker.device_info
        tracker.save()

        return JsonResponse({"status": "success", "device_id": str(device_id)})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


# 🔹 Install Stats (AJAX)
@require_GET
def get_install_stats(request):
    total_installs = InstallTracker.objects.aggregate(total=Sum("install_count"))["total"] or 0
    return JsonResponse({"installs": total_installs})


# 🔹 Contact Form
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