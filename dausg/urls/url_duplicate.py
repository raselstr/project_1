from django.urls import path
from ..views.view_tahun.view_tahun import CopyTahunView

urlpatterns = [
    path("copy-tahun/", CopyTahunView.as_view(), name="copy_tahun_dausg"),
]
