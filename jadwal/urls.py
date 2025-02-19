from django.urls import path 
from jadwal.views import list, simpan, update, delete

app_name = "jadwal"
urlpatterns = [
    path("daftar/", list, name="list"),
    path("simpan/", simpan, name="simpan"),
    path("edit/<int:pk>", update, name="edit"),
    path("delete/<int:pk>", delete, name="delete"),
]