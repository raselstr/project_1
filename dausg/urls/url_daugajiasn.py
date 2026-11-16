from django.urls import path

from ..views.view_daugajiasn import view_daugajiasnprog, view_daugajiasnkeg, view_daugajiasnsub

urlpatterns = [
    path("daugajiasnsub/import", view_daugajiasnsub.upload, name="upload_daugajiasnsub"),
    path("daugajiasnsub/export", view_daugajiasnsub.export, name="export_daugajiasnsub"),
    path("daugajiasnsub/<int:number>/<int:sub>/delete/<int:pk>", view_daugajiasnsub.delete, name="delete_daugajiasnsub"),
    path("daugajiasnsub/<int:number>/<int:sub>/update/<int:pk>", view_daugajiasnsub.update, name="update_daugajiasnsub"),
    path("daugajiasnsub/<int:number>/<int:sub>/simpan", view_daugajiasnsub.simpan, name="simpan_daugajiasnsub"),
    path("daugajiasnsub/<int:number>/<int:sub>/", view_daugajiasnsub.list, name="list_daugajiasnsub"),
    
    path("daugajiasnkeg/import", view_daugajiasnkeg.upload, name="upload_daugajiasnkeg"),
    path("daugajiasnkeg/export", view_daugajiasnkeg.export, name="export_daugajiasnkeg"),
    path("daugajiasnkeg/<int:number>/delete/<int:pk>", view_daugajiasnkeg.delete, name="delete_daugajiasnkeg"),
    path("daugajiasnkeg/<int:number>/update/<int:pk>", view_daugajiasnkeg.update, name="update_daugajiasnkeg"),
    path("daugajiasnkeg/<int:number>/simpan", view_daugajiasnkeg.simpan, name="simpan_daugajiasnkeg"),
    path("daugajiasnkeg/<int:number>/", view_daugajiasnkeg.list, name="list_daugajiasnkeg"),
    
    path("daugajiasnprog/import", view_daugajiasnprog.upload, name="upload_daugajiasnprog"),
    path("daugajiasnprog/export", view_daugajiasnprog.export, name="export_daugajiasnprog"),
    path("daugajiasnprog/delete/<int:pk>", view_daugajiasnprog.delete, name="delete_daugajiasnprog"),
    path("daugajiasnprog/update/<int:pk>", view_daugajiasnprog.update, name="update_daugajiasnprog"),
    path("daugajiasnprog/simpan", view_daugajiasnprog.simpan, name="simpan_daugajiasnprog"),
    path("daugajiasnprog/", view_daugajiasnprog.list, name="list_daugajiasnprog"),
    path("loadprog/", view_daugajiasnprog.load, name="load_daugajiasnprog"),
]
