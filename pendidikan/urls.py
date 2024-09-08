from django.urls import path # type: ignore
from pendidikan.views import view_rencana

urlpatterns = [
    path("rencana/daftar/", view_rencana.list, name="rencana_pendidikan_daftar"),
    path("rencana/filter/", view_rencana.filter, name="rencana_pendidikan_filter"),
    path("rencana/", view_rencana.home, name="rencana_pendidikan_home"),
]