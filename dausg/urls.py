from django.urls import path

from .views import view_dankelprog

urlpatterns = [
    path("delete/<int:pk>", view_dankelprog.delete, name="delete_dankel"),
    path("update/<int:pk>", view_dankelprog.update, name="update_dankel"),
    path("simpan", view_dankelprog.simpan, name="simpan_dankel"),
    path("", view_dankelprog.list, name="list_dankel"),
    path("load/", view_dankelprog.load, name="load_dankelprog"),
    
    
    
]
