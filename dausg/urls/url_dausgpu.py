from django.urls import path

from ..views.view_dausgpu import view_dausgpuprog, view_dausgpukeg, view_dausgpusub

urlpatterns = [
    
    path("dausgpusub/import", view_dausgpusub.upload, name="upload_dausgpusub"),
    path("dausgpusub/export", view_dausgpusub.export, name="export_dausgpusub"),
    path("dausgpusub/<int:number>/<int:sub>/delete/<int:pk>", view_dausgpusub.delete, name="delete_dausgpusub"),
    path("dausgpusub/<int:number>/<int:sub>/update/<int:pk>", view_dausgpusub.update, name="update_dausgpusub"),
    path("dausgpusub/<int:number>/<int:sub>/simpan", view_dausgpusub.simpan, name="simpan_dausgpusub"),
    path("dausgpusub/<int:number>/<int:sub>/", view_dausgpusub.list, name="list_dausgpusub"),
    
    path("dausgpukeg/import", view_dausgpukeg.upload, name="upload_dausgpukeg"),
    path("dausgpukeg/export", view_dausgpukeg.export, name="export_dausgpukeg"),
    path("dausgpukeg/<int:number>/delete/<int:pk>", view_dausgpukeg.delete, name="delete_dausgpukeg"),
    path("dausgpukeg/<int:number>/update/<int:pk>", view_dausgpukeg.update, name="update_dausgpukeg"),
    path("dausgpukeg/<int:number>/simpan", view_dausgpukeg.simpan, name="simpan_dausgpukeg"),
    path("dausgpukeg/<int:number>/", view_dausgpukeg.list, name="list_dausgpukeg"),
    
    path("dausgpuprog/import", view_dausgpuprog.upload, name="upload_dausgpuprog"),
    path("dausgpuprog/export", view_dausgpuprog.export, name="export_dausgpuprog"),
    path("dausgpuprog/delete/<int:pk>", view_dausgpuprog.delete, name="delete_dausgpuprog"),
    path("dausgpuprog/update/<int:pk>", view_dausgpuprog.update, name="update_dausgpuprog"),
    path("dausgpuprog/simpan", view_dausgpuprog.simpan, name="simpan_dausgpuprog"),
    path("dausgpuprog/", view_dausgpuprog.list, name="list_dausgpuprog"),
    path("loadprog/", view_dausgpuprog.load, name="load_dausgpuprog"),
    
]
