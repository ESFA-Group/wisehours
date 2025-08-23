from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.conf import settings

urlpatterns = [
    path("wisehours/admin/", admin.site.urls),
    path("wisehours/api-auth/", include("rest_framework.urls")),
    path("wisehours/", include("sheets.urls")),
    # redirect root to the app prefix explicitly (use absolute path to avoid
    # unexpected relative-resolution to the package name)
    path("", RedirectView.as_view(url="/wisehours/", permanent=True)),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
