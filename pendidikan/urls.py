from django.urls import path
from pendidikan.views import view_rencana

urlpatterns = [
    path("rencana/list/", view_rencana.list, name="rencana_pendidikan_list"),
    path("rencana/filter/", view_rencana.filter, name="rencana_pendidikan_filter"),
    path("rencana/", view_rencana.home, name="rencana_pendidikan_home"),
]