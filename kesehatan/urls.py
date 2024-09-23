from django.urls import path # type: ignore
from kesehatan.views import view_rencana, view_posting, view_realisasi, view_laporan

urlpatterns = [

    path("laporan/pdf/", view_laporan.pdf, name="laporan_kesehatan_pdf"),
    path("laporan/daftar/", view_laporan.list, name="laporan_kesehatan_list"),
    path("laporan/filter/", view_laporan.filter, name="laporan_kesehatan_filter"),
    path("laporan/", view_laporan.home, name="laporan_kesehatan_home"),
    
    path("realisasi/verif/<int:pk>/", view_realisasi.verif, name="realisasi_kesehatan_verif"),
    path("realisasi/modal/<int:pk>/", view_realisasi.modal, name="realisasi_kesehatan_modal"),
    path("realisasi/delete/<int:pk>/", view_realisasi.delete, name="realisasi_kesehatan_delete"),
    path("realisasi/update/<int:pk>/", view_realisasi.update, name="realisasi_kesehatan_update"),
    path("realisasi/simpan/", view_realisasi.simpan, name="realisasi_kesehatan_simpan"),
    path("realisasi/daftar/", view_realisasi.list, name="realisasi_kesehatan_list"),
    path("realisasi/filter/", view_realisasi.filter, name="realisasi_kesehatan_filter"),
    path("realisasi/", view_realisasi.home, name="realisasi_kesehatan_home"),
    
    path("posting/kegiatan", view_posting.posting, name="posting_kesehatan"),
    path("posting/list", view_posting.list, name="posting_kesehatan_list"),
    
    path("rencana/delete/<int:pk>/", view_rencana.delete, name="rencana_kesehatan_delete"),
    path("rencana/update/<int:pk>/", view_rencana.update, name="rencana_kesehatan_update"),
    path("rencana/simpan/", view_rencana.simpan, name="rencana_kesehatan_simpan"),
    path("rencana/daftar/", view_rencana.list, name="rencana_kesehatan_list"),
    path("rencana/filter/", view_rencana.filter, name="rencana_kesehatan_filter"),
    path("rencana/", view_rencana.home, name="rencana_kesehatan_home"),
]