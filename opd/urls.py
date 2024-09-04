from django.urls import path

from .views import view_opd, view_subopd, view_pejabat

urlpatterns = [
    path("import", view_opd.upload, name="upload_opd"),
    path("export", view_opd.export, name="export_opd"),
    path("", view_opd.list, name="list_opd"),
    path("simpan/", view_opd.simpan, name="simpan_opd"),
    path("delete/<int:pk>/", view_opd.delete, name="delete_opd"),
    path("update/<int:pk>/", view_opd.update, name="update_opd"),
    
    path("subopd/import", view_subopd.upload, name="upload_subopd"),
    path("subopd/export", view_subopd.export, name="export_subopd"),
    path("subopd/", view_subopd.list, name="list_subopd"),
    path("subopd/simpan/", view_subopd.simpan, name="simpan_subopd"),
    path("subopd/delete/<int:pk>/", view_subopd.delete, name="delete_subopd"),
    path("subopd/update/<int:pk>/", view_subopd.update, name="update_subopd"),
    
    path("pejabat/", view_pejabat.list, name="list_pejabat"),
    path("pejabat/simpan/", view_pejabat.simpan, name="simpan_pejabat"),
    path("pejabat/delete/<int:pk>/", view_pejabat.delete, name="delete_pejabat"),
    path("pejabat/update/<int:pk>/", view_pejabat.update, name="update_pejabat"),
]
