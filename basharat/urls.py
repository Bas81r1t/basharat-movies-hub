# basharat/urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Custom Admin
from movies.admin import admin_site

# Sitemap
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from movies.models import Movie


class MovieSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Movie.objects.all()

    def location(self, obj):
        return f"/movie/{obj.id}/"


sitemaps = {
    "movies": MovieSitemap,
}

urlpatterns = [
    path("admin/", admin_site.urls),          # ✅ use custom admin
    path("", include("movies.urls")),         # ✅ app urls
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
