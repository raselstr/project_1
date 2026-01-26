from django.urls import path

from . import views

urlpatterns = [
    path("", views.upload_sipd, name="upload_sipd"),
    path("export/", views.export_sipd_excel, name="export_sipd_excel"),

]
