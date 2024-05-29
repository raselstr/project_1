from django.urls import path

# from . import views
from .views import view_dashboard, view_menu, view_submenu, view_level

urlpatterns = [
    path("menu/", view_menu.list_menu, name="list_menu"),
    path("menu/simpan/", view_menu.simpan_menu, name="simpan_menu"),
    path("menu/delete/<int:pk>", view_menu.delete_menu, name="delete_menu"),
    path("menu/update/<int:pk>", view_menu.update_menu, name="update_menu"),

    path("submenu/", view_submenu.list_submenu, name="list_submenu"),
    path("submenu/simpan/", view_submenu.simpan_submenu, name="simpan_submenu"),
    path("submenu/delete/<int:pk>", view_submenu.delete_submenu, name="delete_submenu"),
    path("submenu/update/<int:pk>", view_submenu.update_submenu, name="update_submenu"),
    
    path("level/", view_level.list_level, name="list_level"),
    path("level/simpan/", view_level.simpan_level, name="simpan_level"),
    path("level/delete/<int:pk>", view_level.delete_level, name="delete_level"),
    path("level/update/<int:pk>", view_level.update_level, name="update_level"),

    path("", view_dashboard.index, name="dashboard"),
]
