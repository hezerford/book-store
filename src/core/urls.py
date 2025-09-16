from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("", include("store.urls")),
    path("api/", include("api.urls")),
    path("auth/", include("authentication.urls")),
    path("cart/", include("cart.urls")),
    path("profile/", include("user_profile.urls")),
    path("admin/", admin.site.urls),
    path("captcha/", include("captcha.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
# ] + debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     import debug_toolbar

#     urlpatterns += [
#         path(r"^__debug__/", include(debug_toolbar.urls)),
#     ]
