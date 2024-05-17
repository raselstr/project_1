from django.urls import path

from . import views

urlpatterns = [
    path("", views.opd_list, name="opd_list"),
    
]
