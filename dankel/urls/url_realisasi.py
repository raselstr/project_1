from django.urls import path

from ..views import view_realisasi

urlpatterns = [
    # path('sisadelete/<int:pk>', view_sisa.delete, name="dankelsisa_delete"),
    # path('sisaupdate/<int:pk>', view_sisa.update, name="dankelsisa_update"),
    # path('sisasimpan/', view_sisa.simpan, name="dankelsisa_simpan"),
    path('realtahap/', view_realisasi.list, name="realtahap_list"),
]