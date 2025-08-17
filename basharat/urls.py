"""
URL configuration for basharat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# basharat/urls.py

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ✅ Custom admin import
from movies.admin import admin_site  

# ✅ Sitemap imports
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from movies.models import Movie  

# ✅ Movie Sitemap Class
class MovieSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Movie.objects.all()

    def location(self, obj):
        return f'/movie/{obj.id}/'

# ✅ Sitemaps dictionary
sitemaps = {
    'movies': MovieSitemap,
}

urlpatterns = [
    path("admin/", admin_site.urls),   # <-- yaha change kiya hai
    path("", include("movies.urls")),

    # ✅ Sitemap URL
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

# ✅ Media files serve karne ke liye (images/posters)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
