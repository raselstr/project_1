from django.urls import path

from . import views

urlpatterns = [
    path("", views.upload_sipd, name="upload_sipd"),
    path("progress/<str:task_id>/", views.sipd_import_progress, name="sipd-progress"),
    path("skipped/<int:tahun>/", views.sipd_skipped_view, name="sipd-skipped"),
    path("export/", views.export_sipd_excel, name="export_sipd_excel"),
]
