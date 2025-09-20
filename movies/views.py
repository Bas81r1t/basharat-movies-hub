from django.shortcuts import render, get_object_or_404, redirect
from .models import Playlist, Movie, DownloadLog, InstallTracker, Category
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Sum, Q # <-- Q ko import karo
from itertools import chain # <-- chain ko import karo
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


# 🔹 Home Page (Updated and Simplified)
def home(request):
    query = request.GET.get("q")
    
    # Sabhi playlists aur movies le lo
    all_playlists = Playlist.objects.all()
    all_movies = Movie.objects.all() # Ab unlisted movies alag se lene ki zaroorat nahi

    # Agar search query hai, to filter karo
    if query:
        # Dono models me ek saath search karo
        playlists_q = Q(name__icontains=query)
        movies_q = Q(title__icontains=query)
        
        all_playlists = all_playlists.filter(playlists_q)
        all_movies = all_movies.filter(movies_q)

    # Dono ko ek list me combine karo
    combined_list = list(chain(all_playlists, all_movies))
    
    # Ab 'created_at' ke hisaab se sort karo, newest sabse pehle
    # Jin items me created_at nahi hai (purane data ke liye), unko aakhir me rakhega
    combined_list.sort(key=lambda x: x.created_at or timezone.datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    
    not_found = query and not combined_list

    return render(
        request,
        "home.html",
        {
            "media_items": combined_list, # Hum ab template ko ek hi list bhejenge
            "categories": Category.objects.all(),
            "query": query,
            "not_found": not_found,
        },
    )


# 🔹 Playlist Detail
def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    # Ab movies ko created_at se sort kar sakte hain
    movies = Movie.objects.filter(playlist=playlist).order_by('-created_at')
    return render(request, "playlist_detail.html", {"playlist": playlist, "movies": movies})


# 🔹 Category Detail (FIXED ✅)
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    query = request.GET.get("q")

    movies = Movie.objects.filter(category=category)
    playlists = Playlist.objects.filter(category=category)

    if query:
        movies = movies.filter(title__icontains=query)
        playlists = playlists.filter(name__icontains=query)

    # ✅ Wrapper dict banao
    items = []
    for m in movies:
        items.append({"type": "movie", "obj": m})
    for p in playlists:
        items.append({"type": "playlist", "obj": p})

    # ✅ Sort by created_at
    items.sort(key=lambda x: x["obj"].created_at or timezone.datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    
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
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_for")
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
