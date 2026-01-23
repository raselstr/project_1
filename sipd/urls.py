from django.urls import path

from .views import upload_sipd

urlpatterns = [
    path("", upload_sipd, name="upload_sipd"),
    
]
