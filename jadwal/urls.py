from django.urls import path 
from jadwal.views import list, simpan, update, delete
urlpatterns = [
    path("daftar/", list, name="jadwal_list"),
    path("simpan/", simpan, name="jadwal_simpan"),
    path("edit/<int:pk>", update, name="jadwal_edit"),
    path("delete/<int:pk>", delete, name="jadwal_delete"),
]