from django.urls import path # type: ignore
from pu.views import view_rencana, view_posting, view_realisasi, view_laporan

urlpatterns = [

    path("laporan/apip/", view_laporan.apip, name="laporan_pu_apip"),
    path("laporan/pdf/", view_laporan.pdf, name="laporan_pu_pdf"),
    path("laporan/daftar/", view_laporan.list, name="laporan_pu_list"),
    path("laporan/filter/", view_laporan.filter, name="laporan_pu_filter"),
    path("laporan/", view_laporan.home, name="laporan_pu_home"),
    
    path("realisasi/verif/<int:pk>/", view_realisasi.verif, name="realisasi_pu_verif"),
    path("realisasi/modal/<int:pk>/", view_realisasi.modal, name="realisasi_pu_modal"),
    path("realisasi/delete/<int:pk>/", view_realisasi.delete, name="realisasi_pu_delete"),
    path("realisasi/update/<int:pk>/", view_realisasi.update, name="realisasi_pu_update"),
    path("realisasi/simpan/", view_realisasi.simpan, name="realisasi_pu_simpan"),
    path("realisasi/daftar/", view_realisasi.list, name="realisasi_pu_list"),
    path("realisasi/filter/", view_realisasi.filter, name="realisasi_pu_filter"),
    path("realisasi/", view_realisasi.home, name="realisasi_pu_home"),
    
    path("posting/kegiatan", view_posting.posting, name="posting_pu"),
    path("posting/list", view_posting.list, name="posting_pu_list"),
    
    path("rencana/delete/<int:pk>/", view_rencana.delete, name="rencana_pu_delete"),
    path("rencana/update/<int:pk>/", view_rencana.update, name="rencana_pu_update"),
    path("rencana/simpan/", view_rencana.simpan, name="rencana_pu_simpan"),
    path("rencana/daftar/", view_rencana.list, name="rencana_pu_list"),
    path("rencana/filter/", view_rencana.filter, name="rencana_pu_filter"),
    path("rencana/", view_rencana.home, name="rencana_pu_home"),
]