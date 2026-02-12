from django.urls import path
from . import views

urlpatterns = [
    path("", views.djpk_list, name="djpk_list"),
    path("print/<int:pk>/", views.djpk_print, name="djpk_print"),

]
