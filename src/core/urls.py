from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path("", include("store.urls")),
    path("api/", include("api.urls")),
    path("auth/", include("authentication.urls")),
    path("cart/", include("cart.urls")),
    path("profile/", include("user_profile.urls")),
    path("admin/", admin.site.urls),
] + debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
