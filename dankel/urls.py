from django.urls import path

from . import views

urlpatterns = [
               
    # # path("rencana/delete/<int:pk>", views.delete, name="delete_rencana"),
    # # path("rencana/update/<int:pk>", views.update, name="update_rencana"),
    # path('delete/<int:pk>', views.delete, name="rencdankel_delete"),
    # path('update/<int:pk>', views.update, name="rencdankel_update"),
    path('simpan/', views.simpan, name="dankel_simpan"),
    path('list/', views.list, name="dankel_list"),
    path('', views.home, name='dankel_home'),
    
]