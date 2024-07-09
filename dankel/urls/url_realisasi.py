from django.urls import path

from ..views import view_realisasi

urlpatterns = [
    # path('sisadelete/<int:pk>', view_sisa.delete, name="dankelsisa_delete"),
    # path('sisaupdate/<int:pk>', view_sisa.update, name="dankelsisa_update"),
    path('realisasisimpan/', view_realisasi.simpan, name="realisasidankel_simpan"),
    path('realisasilist/', view_realisasi.list, name="realisasidankel_list"),
    path('realisasidankel/', view_realisasi.filter, name="realisasidankel_filter"),
    path('realisasihome/', view_realisasi.home, name="realisasidankel_home"),
]