from django.urls import path

# from . import views
from .views import view_dashboard, view_menu

urlpatterns = [
    path("menu/", view_menu.list_menu, name="list_menu"),
    path("simpan/", view_menu.simpan_menu, name="simpan_menu"),
    path("delete/<int:pk>", view_menu.delete_menu, name="delete_menu"),
    path("", view_dashboard.index, name="dashboard"),
]
