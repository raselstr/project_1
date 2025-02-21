from django.urls import path # type: ignore
from pendidikan.views import view_rencana, view_posting, view_realisasi, view_laporan, view_rencanasisa, view_postingsisa, view_realisasisisa, view_laporansisa

urlpatterns = [

    path("laporan/sp2d/", view_laporan.sp2d, name="laporan_pendidikan_sp2d"),
    path("laporan/apip/", view_laporan.apip, name="laporan_pendidikan_apip"),
    path("laporan/pdf/", view_laporan.pdf, name="laporan_pendidikan_pdf"),
    path("laporan/daftar/", view_laporan.list, name="laporan_pendidikan_list"),
    path("laporan/filter/", view_laporan.filter, name="laporan_pendidikan_filter"),
    path("laporan/", view_laporan.home, name="laporan_pendidikan_home"),
    
    path("laporansisa/sp2d/", view_laporansisa.sp2d, name="laporan_pendidikan_sp2dsisa"),
    path("laporansisa/apip/", view_laporansisa.apip, name="laporan_pendidikan_apipsisa"),
    path("laporansisa/pdf/", view_laporansisa.pdf, name="laporan_pendidikan_pdfsisa"),
    path("laporansisa/daftar/", view_laporansisa.list, name="laporan_pendidikan_listsisa"),
    path("laporansisa/filter/", view_laporansisa.filter, name="laporan_pendidikan_filtersisa"),
    
    path("realisasi/verif/<int:pk>/", view_realisasi.verif, name="realisasi_pendidikan_verif"),
    path("realisasi/modal/<int:pk>/", view_realisasi.modal, name="realisasi_pendidikan_modal"),
    path("realisasi/delete/<int:pk>/", view_realisasi.delete, name="realisasi_pendidikan_delete"),
    path("realisasi/update/<int:pk>/", view_realisasi.update, name="realisasi_pendidikan_update"),
    path("realisasi/simpan/", view_realisasi.simpan, name="realisasi_pendidikan_simpan"),
    path("realisasi/daftar/", view_realisasi.list, name="realisasi_pendidikan_list"),
    path("realisasi/filter/", view_realisasi.filter, name="realisasi_pendidikan_filter"),
    path("realisasi/", view_realisasi.home, name="realisasi_pendidikan_home"),
    
    path("realisasisisa/verif/<int:pk>/", view_realisasisisa.verif, name="realisasi_pendidikan_verifsisa"),
    path("realisasisisa/modal/<int:pk>/", view_realisasisisa.modal, name="realisasi_pendidikansisa_modal"),
    path("realisasisisa/delete/<int:pk>/", view_realisasisisa.delete, name="realisasi_pendidikansisa_delete"),
    path("realisasisisa/update/<int:pk>/", view_realisasisisa.update, name="realisasi_pendidikansisa_update"),
    path("realisasisisa/simpan/", view_realisasisisa.simpan, name="realisasi_pendidikan_simpansisa"),
    path("realisasisisa/daftar/", view_realisasisisa.list, name="realisasi_pendidikan_listsisa"),
    path("realisasisisa/filter/", view_realisasisisa.filter, name="realisasi_pendidikan_filtersisa"),
    
    path("posting/kegiatan", view_posting.posting, name="posting_pendidikan"),
    path("posting/list", view_posting.list, name="posting_pendidikan_list"),
    
    path("postingsisa/kegiatan", view_postingsisa.posting, name="posting_pendidikansisa"),
    path("postingsisa/list", view_postingsisa.list, name="posting_pendidikan_listsisa"),
    
    path("rencana/satuan/", view_rencana.satuan, name="rencana_pendidikan_satuan"),
    path("rencana/delete/<int:pk>/", view_rencana.delete, name="rencana_pendidikan_delete"),
    path("rencana/update/<int:pk>/", view_rencana.update, name="rencana_pendidikan_update"),
    path("rencana/simpan/", view_rencana.simpan, name="rencana_pendidikan_simpan"),
    path("rencana/daftar/", view_rencana.list, name="rencana_pendidikan_list"),
    path("rencana/filter/", view_rencana.filter, name="rencana_pendidikan_filter"),
    path("rencana/", view_rencana.home, name="rencana_pendidikan_home"),
    
    # Sisa
    path("rencanasisa/delete/<int:pk>/", view_rencanasisa.delete, name="rencana_pendidikansisa_delete"),
    path("rencanasisa/update/<int:pk>/", view_rencanasisa.update, name="rencana_pendidikansisa_update"),
    path("rencanasisa/simpan/", view_rencanasisa.simpan, name="rencana_pendidikansisa_simpan"),
    path("rencanasisa/daftar/", view_rencanasisa.list, name="rencana_pendidikansisa_list"),
    path("rencanasisa/filter/", view_rencanasisa.filter, name="rencana_pendidikansisa_filter"),
]