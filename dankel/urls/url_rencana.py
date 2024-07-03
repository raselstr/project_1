from django.urls import path

from ..views import view_rencana

urlpatterns = [
    path('delete/<int:pk>', view_rencana.delete, name="dankel_delete"),
    path('update/<int:pk>', view_rencana.update, name="dankel_update"),
    path('simpan/', view_rencana.simpan, name="dankel_simpan"),
    path('list/', view_rencana.list, name="dankel_list"),
    path('', view_rencana.home, name='dankel_home'),
]