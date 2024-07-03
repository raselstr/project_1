from django.urls import path

from ..views import view_sisa

urlpatterns = [
    path('sisadelete/<int:pk>', view_sisa.delete, name="dankelsisa_delete"),
    path('sisaupdate/<int:pk>', view_sisa.update, name="dankelsisa_update"),
    path('sisasimpan/', view_sisa.simpan, name="dankelsisa_simpan"),
    path('sisalist/', view_sisa.list, name="dankelsisa_list"),
]