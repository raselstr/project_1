from django.urls import path

from . import views

urlpatterns = [
               
    # path("rencana/delete/<int:pk>", views.delete, name="delete_rencana"),
    # path("rencana/update/<int:pk>", views.update, name="update_rencana"),
    path('simpan/', views.rencdankel_simpan, name="rencdankel_simpan"),
    path('form/', views.rencdankel_form, name="rencdankel_form"),
    path('', views.rencdankel_list, name='rencdankel_list'),
    
]