from django.urls import path

from .views import view_dausg, view_dankelprog, view_dankelkeg

urlpatterns = [
    
    path("dankelkeg/<int:number>/delete/<int:pk>", view_dankelkeg.delete, name="delete_dankelkeg"),
    path("dankelkeg/<int:number>/update/<int:pk>", view_dankelkeg.update, name="update_dankelkeg"),
    path("dankelkeg/<int:number>/simpan", view_dankelkeg.simpan, name="simpan_dankelkeg"),
    # path("dankelkeg/<int:pk>/", view_dankelkeg.load, name="load_dankelkeg"),
    path("dankelkeg/<int:number>/", view_dankelkeg.list, name="list_dankelkeg"),
    
    path("dankelprog/delete/<int:pk>", view_dankelprog.delete, name="delete_dankel"),
    path("dankelprog/update/<int:pk>", view_dankelprog.update, name="update_dankel"),
    path("dankelprog/simpan", view_dankelprog.simpan, name="simpan_dankel"),
    path("dankelprog/", view_dankelprog.list, name="list_dankel"),
    path("loadprog/", view_dankelprog.load, name="load_dankelprog"),
    
    path('', view_dausg.dausg, name='dausg')
    
    
    
]
