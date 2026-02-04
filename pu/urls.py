from django.urls import path # type: ignore
from pu.views import view_rencana, view_rencanasisa, view_posting, view_postingsisa, view_realisasi, view_realisasisisa, view_laporan, view_laporansisa

urlpatterns = [

    path("laporan/sp2d/", view_laporan.sp2d, name="laporan_pu_sp2d"),
    path("laporan/apip/", view_laporan.apip, name="laporan_pu_apip"),
    path("laporan/pdf/", view_laporan.pdf, name="laporan_pu_pdf"),
    path("laporan/daftar/", view_laporan.list, name="laporan_pu_list"),
    path("laporan/filter/", view_laporan.filter, name="laporan_pu_filter"),
    path("laporan/", view_laporan.home, name="laporan_pu_home"),
    
    path("laporansisa/sp2d/", view_laporansisa.sp2d, name="laporan_pu_sp2dsisa"),
    path("laporansisa/apip/", view_laporansisa.apip, name="laporan_pu_apipsisa"),
    path("laporansisa/pdf/", view_laporansisa.pdf, name="laporan_pu_pdfsisa"),
    path("laporansisa/daftar/", view_laporansisa.list, name="laporan_pu_listsisa"),
    path("laporansisa/filter/", view_laporansisa.filter, name="laporan_pu_filtersisa"),
    
    path("realisasi/verif/<int:pk>/", view_realisasi.verif, name="realisasi_pu_verif"),
    path("realisasi/modal/<int:pk>/", view_realisasi.modal, name="realisasi_pu_modal"),
    path("realisasi/delete/<int:pk>/", view_realisasi.delete, name="realisasi_pu_delete"),
    path("realisasi/update/<int:pk>/", view_realisasi.update, name="realisasi_pu_update"),
    path("realisasi/simpan/<int:pk>/", view_realisasi.simpan, name="realisasi_pu_simpan"),
    path("realisasi/daftar/", view_realisasi.list, name="realisasi_pu_list"),
    path("realisasi/sp2d/<int:pk>/", view_realisasi.sp2d, name="realisasi_pu_sp2d"),
    path("realisasi/filter/", view_realisasi.filter, name="realisasi_pu_filter"),
    path("realisasi/", view_realisasi.home, name="realisasi_pu_home"),
    
    path("realisasisisa/verif/<int:pk>/", view_realisasisisa.verif, name="realisasi_pu_verifsisa"),
    path("realisasisisa/modal/<int:pk>/", view_realisasisisa.modal, name="realisasi_pusisa_modal"),
    path("realisasisisa/delete/<int:pk>/", view_realisasisisa.delete, name="realisasi_pusisa_delete"),
    path("realisasisisa/update/<int:pk>/", view_realisasisisa.update, name="realisasi_pusisa_update"),
    path("realisasisisa/simpan/<int:pk>/", view_realisasisisa.simpan, name="realisasi_pu_simpansisa"),
    path("realisasisisa/sp2d/<int:pk>/", view_realisasisisa.sp2d, name="realisasi_pu_sp2dsisa"),
    path("realisasisisa/daftar/", view_realisasisisa.list, name="realisasi_pu_listsisa"),
    path("realisasisisa/filter/", view_realisasisisa.filter, name="realisasi_pu_filtersisa"),
    
    path("posting/kegiatan", view_posting.posting, name="posting_pu"),
    path("posting/list", view_posting.list, name="posting_pu_list"),
    
    path("postingsisa/kegiatan", view_postingsisa.posting, name="posting_pusisa"),
    path("postingsisa/list", view_postingsisa.list, name="posting_pu_listsisa"),
    
    path("rencana/cetak", view_rencana.cetak, name="rencana_pu_cetak"),
    path("rencana/delete/<int:pk>/", view_rencana.delete, name="rencana_pu_delete"),
    path("rencana/update/<int:pk>/", view_rencana.update, name="rencana_pu_update"),
    path("rencana/simpan/", view_rencana.simpan, name="rencana_pu_simpan"),
    path("rencana/daftar/", view_rencana.list, name="rencana_pu_list"),
    path("rencana/filter/", view_rencana.filter, name="rencana_pu_filter"),
    path("rencana/", view_rencana.home, name="rencana_pu_home"),
    
    path("rencanasisa/cetak", view_rencanasisa.cetak, name="rencana_pu_cetaksisa"),
    path("rencanasisa/delete/<int:pk>/", view_rencanasisa.delete, name="rencana_pu_deletesisa"),
    path("rencanasisa/update/<int:pk>/", view_rencanasisa.update, name="rencana_pu_updatesisa"),
    path("rencanasisa/simpan/", view_rencanasisa.simpan, name="rencana_pu_simpansisa"),
    path("rencanasisa/daftar/", view_rencanasisa.list, name="rencana_pu_listsisa"),
    path("rencanasisa/filter/", view_rencanasisa.filter, name="rencana_pu_filtersisa"),
]