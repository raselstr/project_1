from django.urls import path

from ..views import view_laporansisa

urlpatterns = [
    # path('sisadelete/<int:pk>', view_sisa.delete, name="dankelsisa_delete"),
    # path('sisaupdate/<int:pk>', view_sisa.update, name="dankelsisa_update"),
    # path('sisasimpan/', view_sisa.simpan, name="dankelsisa_simpan"),
    path('laporanlistsisa/', view_laporansisa.list, name="laporansisa_list"),
    path('laporanfiltersisa/', view_laporansisa.filter, name="laporansisa_filter"),
]