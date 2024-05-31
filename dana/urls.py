from django.urls import path

from .views import view_dana, view_program, view_kegiatan

urlpatterns = [
    path("", view_dana.list_dana, name="list_dana"),
    path("dana/simpan/", view_dana.simpan_dana, name="simpan_dana"),
    path("dana/delete/<int:pk>", view_dana.delete_dana, name="delete_dana"),
    path("dana/update/<int:pk>", view_dana.update_dana, name="update_dana"),
    
    path("program/", view_program.list_program, name="list_program"),
    path("program/simpan/", view_program.simpan_program, name="simpan_program"),
    path("program/delete/<int:pk>", view_program.delete_program, name="delete_program"),
    path("program/update/<int:pk>", view_program.update_program, name="update_program"),
    
    path("kegiatan/", view_kegiatan.list_kegiatan, name="list_kegiatan"),
    path("kegiatan/simpan/", view_kegiatan.simpan_kegiatan, name="simpan_kegiatan"),
    path("kegiatan/delete/<int:pk>", view_kegiatan.delete_kegiatan, name="delete_kegiatan"),
    path("kegiatan/update/<int:pk>", view_kegiatan.update_kegiatan, name="update_kegiatan"),
    path("kegiatan/load_dana/", view_kegiatan.load_dana, name='load_dana')
    
    
]
