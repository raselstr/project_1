from django.urls import path # type: ignore
from kesehatan.views import view_rencana, view_rencanasisa, view_posting, view_postingsisa, view_realisasi, view_realisasisisa, view_laporan, view_laporansisa

urlpatterns = [

    path("laporan/sp2d/", view_laporan.sp2d, name="laporan_kesehatan_sp2d"),
    path("laporan/apip/", view_laporan.apip, name="laporan_kesehatan_apip"),
    path("laporan/pdf/", view_laporan.pdf, name="laporan_kesehatan_pdf"),
    path("laporan/daftar/", view_laporan.list, name="laporan_kesehatan_list"),
    path("laporan/filter/", view_laporan.filter, name="laporan_kesehatan_filter"),
    path("laporan/", view_laporan.home, name="laporan_kesehatan_home"),
    
    path("laporansisa/sp2d/", view_laporansisa.sp2d, name="laporan_kesehatansisa_sp2d"),
    path("laporansisa/apip/", view_laporansisa.apip, name="laporan_kesehatansisa_apip"),
    path("laporansisa/pdf/", view_laporansisa.pdf, name="laporan_kesehatansisa_pdf"),
    path("laporansisa/daftar/", view_laporansisa.list, name="laporan_kesehatan_listsisa"),
    path("laporansisa/filter/", view_laporansisa.filter, name="laporan_kesehatan_filtersisa"),
    
    path("realisasi/verif/<int:pk>/", view_realisasi.verif, name="realisasi_kesehatan_verif"),
    path("realisasi/modal/<int:pk>/", view_realisasi.modal, name="realisasi_kesehatan_modal"),
    path("realisasi/delete/<int:pk>/", view_realisasi.delete, name="realisasi_kesehatan_delete"),
    path("realisasi/update/<int:pk>/", view_realisasi.update, name="realisasi_kesehatan_update"),
    path("realisasi/simpan/", view_realisasi.simpan, name="realisasi_kesehatan_simpan"),
    path("realisasi/daftar/", view_realisasi.list, name="realisasi_kesehatan_list"),
    path("realisasi/filter/", view_realisasi.filter, name="realisasi_kesehatan_filter"),
    path("realisasi/", view_realisasi.home, name="realisasi_kesehatan_home"),
    
    path("realisasisisa/verif/<int:pk>/", view_realisasisisa.verif, name="realisasi_kesehatan_verifsisa"),
    path("realisasisisa/modal/<int:pk>/", view_realisasisisa.modal, name="realisasi_kesehatansisa_modal"),
    path("realisasisisa/delete/<int:pk>/", view_realisasisisa.delete, name="realisasi_kesehatansisa_delete"),
    path("realisasisisa/update/<int:pk>/", view_realisasisisa.update, name="realisasi_kesehatansisa_update"),
    path("realisasisisa/simpan/", view_realisasisisa.simpan, name="realisasi_kesehatan_simpansisa"),
    path("realisasisisa/daftar/", view_realisasisisa.list, name="realisasi_kesehatan_listsisa"),
    path("realisasisisa/filter/", view_realisasisisa.filter, name="realisasi_kesehatan_filtersisa"),
    
    path("posting/kegiatan", view_posting.posting, name="posting_kesehatan"),
    path("posting/list", view_posting.list, name="posting_kesehatan_list"),
    
    path("postingsisa/kegiatan", view_postingsisa.posting, name="posting_kesehatansisa"),
    path("postingsisa/list", view_postingsisa.list, name="posting_kesehatan_listsisa"),
    
    path("rencana/delete/<int:pk>/", view_rencana.delete, name="rencana_kesehatan_delete"),
    path("rencana/update/<int:pk>/", view_rencana.update, name="rencana_kesehatan_update"),
    path("rencana/simpan/", view_rencana.simpan, name="rencana_kesehatan_simpan"),
    path("rencana/daftar/", view_rencana.list, name="rencana_kesehatan_list"),
    path("rencana/filter/", view_rencana.filter, name="rencana_kesehatan_filter"),
    path("rencana/", view_rencana.home, name="rencana_kesehatan_home"),
    
    path("rencanasisa/delete/<int:pk>/", view_rencanasisa.delete, name="rencana_kesehatan_deletesisa"),
    path("rencanasisa/update/<int:pk>/", view_rencanasisa.update, name="rencana_kesehatan_updatesisa"),
    path("rencanasisa/simpan/", view_rencanasisa.simpan, name="rencana_kesehatan_simpansisa"),
    path("rencanasisa/daftar/", view_rencanasisa.list, name="rencana_kesehatan_listsisa"),
    path("rencanasisa/filter/", view_rencanasisa.filter, name="rencana_kesehatan_filtersisa"),
]