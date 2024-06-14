from django.urls import path

from . import views

urlpatterns = [
               
    # path("rencana/delete/<int:pk>", views.delete, name="delete_rencana"),
    # path("rencana/update/<int:pk>", views.update, name="update_rencana"),
    # path("rencana/simpan", views.simpan, name="simpan_rencana"),
    path("form/", views.rencdankel_form, name="form_dankel"),
    path('', views.rencdankel_list, name='rencdankel_list'),
    
]