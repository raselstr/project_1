from django.urls import path

from .views import view_penerimaan, view_distribusi

urlpatterns = [
               
    path("penerimaan/delete/<int:pk>", view_penerimaan.delete, name="delete_penerimaan"),
    path("penerimaan/update/<int:pk>", view_penerimaan.update, name="update_penerimaan"),
    path("penerimaan/simpan", view_penerimaan.simpan, name="simpan_penerimaan"),
    path("penerimaan/", view_penerimaan.list, name="list_penerimaan"),
    
    path("distribusi/<int:number>/delete/<int:pk>", view_distribusi.delete, name="delete_distribusi"),
    path("distribusi/<int:number>/update/<int:pk>", view_distribusi.update, name="update_distribusi"),
    path("distribusi/<int:number>/simpan", view_distribusi.simpan, name="simpan_distribusi"),
    path("distribusi/<int:number>", view_distribusi.list, name="list_distribusi"),
    
]
