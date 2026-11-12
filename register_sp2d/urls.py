from django.urls import path
from . import views

urlpatterns = [
    path("",           views.upload_register_sp2d, name="register_sp2d"),
    path("progress/<str:task_id>/", views.register_sp2d_progress, name="register_sp2d_progress"),
    path("export/",    views.export_register_sp2d, name="register_sp2d_export"),
]
