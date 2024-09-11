from django.urls import path
from . import views

urlpatterns = [
    path("", views.list, name="list_pagudausg"),
    path("simpan/", views.simpan, name="simpan_pagudausg"),
    path("delete/<int:pk>", views.delete, name="delete_pagudausg"),
    path("update/<int:pk>", views.update, name="update_pagudausg"),
    path("eksport/", views.export, name="eksport_pagudausg"),
    path("upload/", views.upload, name="upload_pagudausg"),
]
