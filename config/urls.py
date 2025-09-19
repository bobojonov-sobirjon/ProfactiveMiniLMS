from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from apps.website import views

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('', include('apps.website.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('courses/', include('apps.courses.urls')),
    path('order/', include('apps.order.urls')),
]

# Serve static files - serve from staticfiles directory
if settings.DEBUG or not settings.DEBUG:  # Always serve static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT, }, ), ]

# Custom 404 handler
handler404 = views.custom_404
