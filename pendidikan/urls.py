from django.urls import path # type: ignore
from pendidikan.views import view_rencana, view_posting, view_realisasi, view_laporan

urlpatterns = [

    path("laporan/apip/", view_laporan.apip, name="laporan_pendidikan_apip"),
    path("laporan/pdf/", view_laporan.pdf, name="laporan_pendidikan_pdf"),
    path("laporan/daftar/", view_laporan.list, name="laporan_pendidikan_list"),
    path("laporan/filter/", view_laporan.filter, name="laporan_pendidikan_filter"),
    path("laporan/", view_laporan.home, name="laporan_pendidikan_home"),
    
    path("realisasi/verif/<int:pk>/", view_realisasi.verif, name="realisasi_pendidikan_verif"),
    path("realisasi/modal/<int:pk>/", view_realisasi.modal, name="realisasi_pendidikan_modal"),
    path("realisasi/delete/<int:pk>/", view_realisasi.delete, name="realisasi_pendidikan_delete"),
    path("realisasi/update/<int:pk>/", view_realisasi.update, name="realisasi_pendidikan_update"),
    path("realisasi/simpan/", view_realisasi.simpan, name="realisasi_pendidikan_simpan"),
    path("realisasi/daftar/", view_realisasi.list, name="realisasi_pendidikan_list"),
    path("realisasi/filter/", view_realisasi.filter, name="realisasi_pendidikan_filter"),
    path("realisasi/", view_realisasi.home, name="realisasi_pendidikan_home"),
    
    path("posting/kegiatan", view_posting.posting, name="posting_pendidikan"),
    path("posting/list", view_posting.list, name="posting_pendidikan_list"),
    
    path("rencana/delete/<int:pk>/", view_rencana.delete, name="rencana_pendidikan_delete"),
    path("rencana/update/<int:pk>/", view_rencana.update, name="rencana_pendidikan_update"),
    path("rencana/simpan/", view_rencana.simpan, name="rencana_pendidikan_simpan"),
    path("rencana/daftar/", view_rencana.list, name="rencana_pendidikan_list"),
    path("rencana/filter/", view_rencana.filter, name="rencana_pendidikan_filter"),
    path("rencana/", view_rencana.home, name="rencana_pendidikan_home"),
]