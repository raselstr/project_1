from django.urls import path

from .views import view_opd, view_subopd

urlpatterns = [
    path("", view_opd.list, name="list_opd"),
    path("simpan/", view_opd.simpan, name="simpan_opd"),
    path("delete/<int:pk>/", view_opd.delete, name="delete_opd"),
    path("update/<int:pk>/", view_opd.update, name="update_opd"),
    
    path("subopd/", view_subopd.list, name="list_subopd"),
    path("subopd/simpan/", view_subopd.simpan, name="simpan_subopd"),
    path("subopd/delete/<int:pk>/", view_subopd.delete, name="delete_subopd"),
    path("subopd/update/<int:pk>/", view_subopd.update, name="update_subopd"),
]
