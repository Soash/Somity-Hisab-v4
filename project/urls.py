from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app1.urls')),
    path('', include('primary_setup.urls')),
    path('', include('otrans.urls')),
    path('report/', include('report.urls')),
    path('sheet/', include('sheet.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('sms/', include('sms.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)