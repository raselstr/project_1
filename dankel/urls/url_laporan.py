from django.urls import path

from ..views import view_laporan

urlpatterns = [
    # path('sisadelete/<int:pk>', view_sisa.delete, name="dankelsisa_delete"),
    # path('sisaupdate/<int:pk>', view_sisa.update, name="dankelsisa_update"),
    # path('sisasimpan/', view_sisa.simpan, name="dankelsisa_simpan"),
    path('laporanlist/', view_laporan.list, name="laporan_list"),
    path('laporanfilter/', view_laporan.filter, name="laporan_filter"),
    path('laporanhome/', view_laporan.home, name="laporan_home"),
]