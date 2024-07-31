from django.urls import path

from ..views import view_realisasi

urlpatterns = [
    path('realisasidelete/<int:pk>', view_realisasi.delete, name="realisasidanke_delete"),
    path('realisasiupdate/<int:pk>', view_realisasi.update, name="realisasidanke_update"),
    path('realisasisimpan/', view_realisasi.simpan, name="realisasidankel_simpan"),
    path('realisasilist/', view_realisasi.list, name="realisasidankel_list"),
    path('realisasidankel/', view_realisasi.filter, name="realisasidankel_filter"),
    path('realisasihome/', view_realisasi.home, name="realisasidankel_home"),
]