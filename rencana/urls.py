from django.urls import path

from . import views

urlpatterns = [
               
    path("rencana/delete/<int:pk>", views.delete, name="delete_rencana"),
    path("rencana/update/<int:pk>", views.update, name="update_rencana"),
    path("rencana/simpan", views.simpan, name="simpan_rencana"),
    path("rencana/", views.list, name="list_rencana"),
    
]
