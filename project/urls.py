from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    
    path('pu/', include('pu.urls')),
    path('kesehatan/', include('kesehatan.urls')),
    path('pendidikan/', include('pendidikan.urls')),
    path('jadwal/', include('jadwal.urls')),
    
    path('pagudausg/', include('pagu.urls')),
    path('dankel/', include('dankel.urls.url_realisasi')),
    path('dankel/', include('dankel.urls.url_realisasisisa')),
    path('dankel/', include('dankel.urls.url_rencana')),
    path('dankel/', include('dankel.urls.url_sisa')),
    path('dankel/', include('dankel.urls.url_laporan')),
    path('dankel/', include('dankel.urls.url_laporansisa')),
    path('dankel/', include('dankel.urls.url_posting')),
    path('dankel/', include('dankel.urls.url_postingsisa')),
    path('penerimaan/', include('penerimaan.urls')),
    path('dausg/dankel/', include('dausg.urls.url_dankel')),
    path('dausg/dausgpend/', include('dausg.urls.url_dausgpend')),
    path('dausg/dausgkes/', include('dausg.urls.url_dausgkes')),
    path('dausg/dausgpu/', include('dausg.urls.url_dausgpu')),
    path('dana/', include('dana.urls')),
    path('opd/', include('opd.urls')),
    path('notfound/', views.notfound,name='notfound'),
    path('', include('dashboard.urls')),
    path('auth/', include('authapp.urls')),
    path('admin/', admin.site.urls),
    
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
