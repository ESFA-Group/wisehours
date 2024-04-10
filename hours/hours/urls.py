from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
import debug_toolbar

urlpatterns = [
    path("hour/admin/", admin.site.urls),
    path("hour/api-auth/", include("rest_framework.urls")),
    path("", include("sheets.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
