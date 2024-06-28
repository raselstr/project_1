from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('pagudausg/', include('pagu.urls')),
    path('dankel/', include('dankel.urls')),
    path('penerimaan/', include('penerimaan.urls')),
    path('dausg/dankel/', include('dausg.urls.url_dankel')),
    path('dausg/dausgpend/', include('dausg.urls.url_dausgpend')),
    path('dausg/dausgkes/', include('dausg.urls.url_dausgkes')),
    path('dausg/dausgpu/', include('dausg.urls.url_dausgpu')),
    path('dana/', include('dana.urls')),
    path('opd/', include('opd.urls')),
    path('', include('dashboard.urls')),
    path('admin/', admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
