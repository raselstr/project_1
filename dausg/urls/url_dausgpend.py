from django.urls import path

from ..views.view_dausg import view_dausg
from ..views.view_dausgpendidikan import view_dausgpendidikanprog, view_dausgpendidikankeg, view_dausgpendidikansub

urlpatterns = [
    
    path("dausgpendidikansub/<int:number>/<int:sub>/delete/<int:pk>", view_dausgpendidikansub.delete, name="delete_dausgpendidikansub"),
    path("dausgpendidikansub/<int:number>/<int:sub>/update/<int:pk>", view_dausgpendidikansub.update, name="update_dausgpendidikansub"),
    path("dausgpendidikansub/<int:number>/<int:sub>/simpan", view_dausgpendidikansub.simpan, name="simpan_dausgpendidikansub"),
    path("dausgpendidikansub/<int:number>/<int:sub>/", view_dausgpendidikansub.list, name="list_dausgpendidikansub"),
    
    path("dausgpendidikankeg/<int:number>/delete/<int:pk>", view_dausgpendidikankeg.delete, name="delete_dausgpendidikankeg"),
    path("dausgpendidikankeg/<int:number>/update/<int:pk>", view_dausgpendidikankeg.update, name="update_dausgpendidikankeg"),
    path("dausgpendidikankeg/<int:number>/simpan", view_dausgpendidikankeg.simpan, name="simpan_dausgpendidikankeg"),
    path("dausgpendidikankeg/<int:number>/", view_dausgpendidikankeg.list, name="list_dausgpendidikankeg"),
    
    path("dausgpendidikanprog/delete/<int:pk>", view_dausgpendidikanprog.delete, name="delete_dausgpendidikanprog"),
    path("dausgpendidikanprog/update/<int:pk>", view_dausgpendidikanprog.update, name="update_dausgpendidikanprog"),
    path("dausgpendidikanprog/simpan", view_dausgpendidikanprog.simpan, name="simpan_dausgpendidikanprog"),
    path("dausgpendidikanprog/", view_dausgpendidikanprog.list, name="list_dausgpendidikanprog"),
    path("loadprog/", view_dausgpendidikanprog.load, name="load_dausgpendidikanprog"),
    
]