# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload_sipd, name="upload_sipd"),
    path("progress/<str:task_id>/", views.sipd_import_progress, name="sipd-progress"),
    path("skipped/<int:tahun>/", views.skipped_sipd_view, name="sipd-skipped"),
    path("log/", views.sipd_log_view, name="sipd_log"),
    path("export/", views.export_sipd_excel, name="export_sipd_excel"),

    path("tbp/", views.upload_tbp, name="upload_tbp"),
    path("tbp/progress/<str:task_id>/", views.tbp_import_progress, name="tbp-progress"),
    path("tbp/log/", views.tbp_log_view, name="tbp_log"),
    path("tbp/export/", views.export_tbp_excel, name="export_tbp_excel"),
    
    path("dokumen/<str:mode>/<int:pk>/", views.view_sipd, name="data_sipd"),
    path('modal-output/', views.modal_output, name='modal_output'),
    path("monitor/", views.monitor_sipd, name="monitor_sipd"),
    path("monitor/detail/", views.monitor_sipd_detail, name="monitor_sipd_detail"),
    path("monitor/print/", views.monitor_sipd_print, name="monitor_sipd_print"),
]
