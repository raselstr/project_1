from django.urls import path
from core.views import view_laporan_sp2d

urlpatterns = [
    path('sp2d/', view_laporan_sp2d.laporan_sp2d_rekap, name='laporan_sp2d_rekap'),
    path('sp2d/cetak/', view_laporan_sp2d.laporan_sp2d_rekap_cetak, name='laporan_sp2d_rekap_cetak'),
    path('sp2d/excel/', view_laporan_sp2d.laporan_sp2d_rekap_excel, name='laporan_sp2d_rekap_excel'),
]

