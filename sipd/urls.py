# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload_sipd, name="upload_sipd"),
    path("progress/<task_id>/", views.sipd_import_progress, name="sipd-progress"),
    path("skipped/<int:tahun>/", views.skipped_sipd_view, name="sipd-skipped"),
    path("export/", views.export_sipd_excel, name="export_sipd_excel"),

    path("tbp/", views.upload_tbp, name="upload_tbp"),
    path("tbp/progress/<task_id>/", views.tbp_import_progress, name="tbp-progress"),
    path("tbp/export/", views.export_tbp_excel, name="export_tbp_excel"),
    
    path("dokumen/<str:mode>/<int:pk>/", views.view_sipd, name="data_sipd"),

]