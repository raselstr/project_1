from django.urls import path # type: ignore
from pendidikan.views import view_rencana

urlpatterns = [
    path("rencana/delete/<int:pk>/", view_rencana.delete, name="rencana_pendidikan_delete"),
    path("rencana/update/<int:pk>/", view_rencana.update, name="rencana_pendidikan_update"),
    path("rencana/simpan/", view_rencana.simpan, name="rencana_pendidikan_simpan"),
    path("rencana/daftar/", view_rencana.list, name="rencana_pendidikan_list"),
    path("rencana/filter/", view_rencana.filter, name="rencana_pendidikan_filter"),
    path("rencana/", view_rencana.home, name="rencana_pendidikan_home"),
]