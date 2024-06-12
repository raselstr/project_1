from django.urls import path

from . import views

urlpatterns = [
               
    path("penerimaan/delete/<int:pk>", views.delete, name="delete_penerimaan"),
    path("penerimaan/update/<int:pk>", views.update, name="update_penerimaan"),
    path("penerimaan/simpan", views.simpan, name="simpan_penerimaan"),
    path("penerimaan/", views.list, name="list_penerimaan"),
    
]
