from django.urls import path

from ..views import view_laporan

urlpatterns = [
    path('laporanpdf/', view_laporan.pdf, name="laporan_pdf"),
    path('laporanlist/', view_laporan.list, name="laporan_list"),
    path('laporanfilter/', view_laporan.filter, name="laporan_filter"),
    path('laporanhome/', view_laporan.home, name="laporan_home"),
]