from django.urls import path

from . import views

urlpatterns = [
    path("", views.opd_list, name="opd_list"),
    path("tambah_opd/", views.form_opd, name="tambah_opd"),
    path("simpan_opd/", views.simpan_opd, name="simpan_opd"),
    path("delete_opd/<int:opd_id>/", views.delete_opd, name="delete_opd"),
]
