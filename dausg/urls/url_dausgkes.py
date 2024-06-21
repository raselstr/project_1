from django.urls import path

from ..views.view_dausgkesehatan import view_dausgkesehatanprog, view_dausgkesehatankeg, view_dausgkesehatansub

urlpatterns = [
    
    path("dausgkesehatansub/<int:number>/<int:sub>/delete/<int:pk>", view_dausgkesehatansub.delete, name="delete_dausgkesehatansub"),
    path("dausgkesehatansub/<int:number>/<int:sub>/update/<int:pk>", view_dausgkesehatansub.update, name="update_dausgkesehatansub"),
    path("dausgkesehatansub/<int:number>/<int:sub>/simpan", view_dausgkesehatansub.simpan, name="simpan_dausgkesehatansub"),
    path("dausgkesehatansub/<int:number>/<int:sub>/", view_dausgkesehatansub.list, name="list_dausgkesehatansub"),
    
    path("dausgkesehatankeg/<int:number>/delete/<int:pk>", view_dausgkesehatankeg.delete, name="delete_dausgkesehatankeg"),
    path("dausgkesehatankeg/<int:number>/update/<int:pk>", view_dausgkesehatankeg.update, name="update_dausgkesehatankeg"),
    path("dausgkesehatankeg/<int:number>/simpan", view_dausgkesehatankeg.simpan, name="simpan_dausgkesehatankeg"),
    path("dausgkesehatankeg/<int:number>/", view_dausgkesehatankeg.list, name="list_dausgkesehatankeg"),
    
    path("dausgkesehatanprog/delete/<int:pk>", view_dausgkesehatanprog.delete, name="delete_dausgkesehatanprog"),
    path("dausgkesehatanprog/update/<int:pk>", view_dausgkesehatanprog.update, name="update_dausgkesehatanprog"),
    path("dausgkesehatanprog/simpan", view_dausgkesehatanprog.simpan, name="simpan_dausgkesehatanprog"),
    path("dausgkesehatanprog/", view_dausgkesehatanprog.list, name="list_dausgkesehatanprog"),
    path("loadprog/", view_dausgkesehatanprog.load, name="load_dausgkesehatanprog"),
    
]
