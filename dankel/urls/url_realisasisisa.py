from django.urls import path

from ..views import view_realisasisisa

urlpatterns = [
    path('sisamodal_content/<int:pk>/', view_realisasisisa.modal_content, name='modalsisa_content'),
    path('sisatoggle-verif/<int:pk>/', view_realisasisisa.verif, name='togglesisa_verif'),
    path('realisasisisadelete/<int:pk>', view_realisasisisa.delete, name="realisasisisadankel_delete"),
    path('realisasisisaupdate/<int:pk>', view_realisasisisa.update, name="realisasisisadankel_update"),
    path('realisasisisasimpan/', view_realisasisisa.simpan, name="realisasisisadankel_simpan"),
    path('realisasisisalist/', view_realisasisisa.list, name="realisasisisadankel_list"),
    path('realisasisisadankel/', view_realisasisisa.filter, name="realisasisisadankel_filter"),
]