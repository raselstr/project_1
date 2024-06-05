from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dausg/', include('dausg.urls')),
    path('dana/', include('dana.urls')),
    path('opd/', include('opd.urls')),
    path('', include('dashboard.urls')),
    path('admin/', admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
