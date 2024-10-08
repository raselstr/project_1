from django.urls import path

from ..views.view_dausg import view_dausg
from ..views.view_dankel import view_dankelprog, view_dankelkeg, view_dankelsub

urlpatterns = [
    
    path("dankelsub/import", view_dankelsub.upload, name="upload_dankelsub"),
    path("dankelsub/export", view_dankelsub.export, name="export_dankelsub"),
    path("dankelsub/<int:number>/<int:sub>/delete/<int:pk>", view_dankelsub.delete, name="delete_dankelsub"),
    path("dankelsub/<int:number>/<int:sub>/update/<int:pk>", view_dankelsub.update, name="update_dankelsub"),
    path("dankelsub/<int:number>/<int:sub>/simpan", view_dankelsub.simpan, name="simpan_dankelsub"),
    path("dankelsub/<int:number>/<int:sub>/", view_dankelsub.list, name="list_dankelsub"),
    
    path("dankelkeg/import", view_dankelkeg.upload, name="upload_dankelkeg"),
    path("dankelkeg/export", view_dankelkeg.export, name="export_dankelkeg"),
    path("dankelkeg/<int:number>/delete/<int:pk>", view_dankelkeg.delete, name="delete_dankelkeg"),
    path("dankelkeg/<int:number>/update/<int:pk>", view_dankelkeg.update, name="update_dankelkeg"),
    path("dankelkeg/<int:number>/simpan", view_dankelkeg.simpan, name="simpan_dankelkeg"),
    path("dankelkeg/<int:number>/", view_dankelkeg.list, name="list_dankelkeg"),
    
    path("dankelprog/import", view_dankelprog.upload, name="upload_dankel"),
    path("dankelprog/export", view_dankelprog.export, name="export_dankel"),
    path("dankelprog/delete/<int:pk>", view_dankelprog.delete, name="delete_dankel"),
    path("dankelprog/update/<int:pk>", view_dankelprog.update, name="update_dankel"),
    path("dankelprog/simpan", view_dankelprog.simpan, name="simpan_dankel"),
    path("dankelprog/", view_dankelprog.list, name="list_dankel"),
    path("loadprog/", view_dankelprog.load, name="load_dankelprog"),
    
    path('', view_dausg.dausg, name='dausg')
    
    
    

]
