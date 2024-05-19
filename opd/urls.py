from django.urls import path

from . import views

urlpatterns = [
    path("", views.opd_list, name="opd_list"),
    path("simpan_opd/", views.simpan_opd, name="simpan_opd"),
    
]
