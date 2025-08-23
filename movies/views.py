from django.shortcuts import render, get_object_or_404, redirect
from .models import Playlist, Movie, DownloadLog, InstallTracker
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import json
import re

# ------------------------
# Helper: Extract Episode Number
# ------------------------
def extract_episode_number(title):
    match = re.search(r'[Ee]pisode\s*(\d+)', title)
    if match:
        return int(match.group(1))
    match = re.search(r'\d+', title)
    if match:
        return int(match.group())
    return float('inf')

# ------------------------
# Home Page
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

# ------------------------
# Playlist Details
# ------------------------
def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    movies = Movie.objects.filter(playlist=playlist)
    movies = sorted(movies, key=lambda m: extract_episode_number(m.title))
    return render(request, 'playlist_detail.html', {'playlist': playlist, 'movies': movies})

# ------------------------
# Movie Detail Page
# ------------------------
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movie_detail.html', {'movie': movie})

# ------------------------
# Helper: Get Client IP
# ------------------------
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

# ------------------------
# Download Movie + Log
# ------------------------
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
        username=username,
        download_time=timezone.now()
    )
    return redirect(movie.download_link)

# ------------------------
# PWA Install/Delete Tracking
# ------------------------
@csrf_exempt
def track_install(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            device = data.get("device", "Unknown device")
            action = data.get("action", "install")

            tracker, created = InstallTracker.objects.get_or_create(device_info=device)

            if action == "install":
                tracker.installed = True
                tracker.install_count += 1
                tracker.last_action = "install"

            elif action == "delete":
                tracker.installed = False
                tracker.delete_count += 1
                tracker.last_action = "delete"

            tracker.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "fail"})

@require_GET
def get_install_stats(request):
    total_installs = InstallTracker.objects.filter(installed=True).count()
    total_deletes = InstallTracker.objects.filter(last_action="delete").count()

    return JsonResponse({
        "installs": total_installs,
        "deletes": total_deletes,
    })

# ------------------------
# Contact Form
# ------------------------
def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

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
