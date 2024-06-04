from django.urls import path
from .utils import dataprogram

from .views import view_dana, view_program, view_kegiatan, view_subkegiatan, view_subrinc

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
    path("kegiatan/load_program/", view_kegiatan.load_program, name='load_program'),
    
    path("subkegiatan/", view_subkegiatan.list_subkegiatan, name="list_subkegiatan"),
    path("subkegiatan/simpan/", view_subkegiatan.simpan_subkegiatan, name="simpan_subkegiatan"),
    path("subkegiatan/delete/<int:pk>", view_subkegiatan.delete_subkegiatan, name="delete_subkegiatan"),
    path("subkegiatan/update/<int:pk>", view_subkegiatan.update_subkegiatan, name="update_subkegiatan"),
    path("subkegiatan/load_program/", view_subkegiatan.load_kegprogram, name='load_kegprogram'),
    path("subkegiatan/load_kegiatan/", view_subkegiatan.load_kegiatan, name='load_kegiatan'),
    
    path("subrinc/", view_subrinc.list_subrinc, name="list_subrinc"),
    path("subrinc/simpan/", view_subrinc.simpan_subrinc, name="simpan_subrinc"),
    path("subrinc/delete/<int:pk>", view_subrinc.delete_subrinc, name="delete_subrinc"),
    path("subrinc/update/<int:pk>", view_subrinc.update_subrinc, name="update_subrinc"),
    path("subrinc/load_program/", view_subrinc.load_kegprogram, name='load_subrincprogram'),
    path("subrinc/load_kegiatan/", view_subrinc.load_kegiatan, name='load_subrinckegiatan'),
    path("subrinc/load_subkegiatan/", view_subrinc.load_subkegiatan, name='load_subrinckegiatan'),
    
]
