from django.urls import path

from . import views

urlpatterns = [
    path("", views.opd_list, name="opd_list"),
    path("simpan_opd/", views.simpan_opd, name="simpan_opd"),
    path("delete_opd/<int:pk>/", views.delete_opd, name="delete_opd"),
    path("update_opd/<int:pk>/", views.update_opd, name="update_opd"),
    path("books/create/", views.book_create, name="book_create"),
    path("books/", views.book_list, name="book_list"),
]
