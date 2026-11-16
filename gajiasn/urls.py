from django.urls import path  # type: ignore
from gajiasn.views import (
    view_rencana,
    view_rencanasisa,
    view_posting,
    view_postingsisa,
    view_realisasi,
    view_realisasisisa,
    view_laporan,
    view_laporansisa,
)

urlpatterns = [
    # Laporan Utama
    path("laporan/sp2d/", view_laporan.sp2d, name="laporan_gajiasn_sp2d"),
    path("laporan/apip/", view_laporan.apip, name="laporan_gajiasn_apip"),
    path("laporan/excel/", view_laporan.excel, name="laporan_gajiasn_excel"),
    path("laporan/pdf/", view_laporan.pdf, name="laporan_gajiasn_pdf"),
    path("laporan/daftar/", view_laporan.list, name="laporan_gajiasn_list"),
    path("laporan/filter/", view_laporan.filter, name="laporan_gajiasn_filter"),
    path("laporan/", view_laporan.home, name="laporan_gajiasn_home"),

    # Laporan Sisa
    path("laporansisa/sp2d/", view_laporansisa.sp2d, name="laporan_gajiasn_sp2dsisa"),
    path("laporansisa/apip/", view_laporansisa.apip, name="laporan_gajiasn_apipsisa"),
    path("laporansisa/excel/", view_laporansisa.excel, name="laporan_gajiasn_excelsisa"),
    path("laporansisa/pdf/", view_laporansisa.pdf, name="laporan_gajiasn_pdfsisa"),
    path("laporansisa/daftar/", view_laporansisa.list, name="laporan_gajiasn_listsisa"),
    path("laporansisa/filter/", view_laporansisa.filter, name="laporan_gajiasn_filtersisa"),

    # Realisasi Utama
    path("realisasi/verif/<int:pk>/", view_realisasi.verif, name="realisasi_gajiasn_verif"),
    path("realisasi/modal/<int:pk>/", view_realisasi.modal, name="realisasi_gajiasn_modal"),
    path("realisasi/delete/<int:pk>/", view_realisasi.delete, name="realisasi_gajiasn_delete"),
    path("realisasi/update/<int:pk>/", view_realisasi.update, name="realisasi_gajiasn_update"),
    path("realisasi/simpan/<int:pk>/", view_realisasi.simpan, name="realisasi_gajiasn_simpan"),
    path("realisasi/daftar/", view_realisasi.list, name="realisasi_gajiasn_list"),
    path("realisasi/sp2d/<int:pk>/", view_realisasi.sp2d, name="realisasi_gajiasn_sp2d"),
    path("realisasi/filter/", view_realisasi.filter, name="realisasi_gajiasn_filter"),
    path("realisasi/", view_realisasi.home, name="realisasi_gajiasn_home"),

    # Realisasi Sisa
    path("realisasisisa/verif/<int:pk>/", view_realisasisisa.verif, name="realisasi_gajiasn_verifsisa"),
    path("realisasisisa/modal/<int:pk>/", view_realisasisisa.modal, name="realisasi_gajiasnsisa_modal"),
    path("realisasisisa/delete/<int:pk>/", view_realisasisisa.delete, name="realisasi_gajiasnsisa_delete"),
    path("realisasisisa/update/<int:pk>/", view_realisasisisa.update, name="realisasi_gajiasnsisa_update"),
    path("realisasisisa/simpan/<int:pk>/", view_realisasisisa.simpan, name="realisasi_gajiasn_simpansisa"),
    path("realisasisisa/sp2d/<int:pk>/", view_realisasisisa.sp2d, name="realisasi_gajiasn_sp2dsisa"),
    path("realisasisisa/daftar/", view_realisasisisa.list, name="realisasi_gajiasn_listsisa"),
    path("realisasisisa/filter/", view_realisasisisa.filter, name="realisasi_gajiasn_filtersisa"),

    # Posting
    path("posting/kegiatan", view_posting.posting, name="posting_gajiasn"),
    path("posting/list", view_posting.list, name="posting_gajiasn_list"),
    path("postingsisa/kegiatan", view_postingsisa.posting, name="posting_gajiasnsisa"),
    path("postingsisa/list", view_postingsisa.list, name="posting_gajiasn_listsisa"),

    # Rencana Utama
    path("rencana/cetak", view_rencana.cetak, name="rencana_gajiasn_cetak"),
    path("rencana/excel/", view_rencana.excel, name="rencana_gajiasn_excel"),
    path("rencana/delete/<int:pk>/", view_rencana.delete, name="rencana_gajiasn_delete"),
    path("rencana/update/<int:pk>/", view_rencana.update, name="rencana_gajiasn_update"),
    path("rencana/simpan/", view_rencana.simpan, name="rencana_gajiasn_simpan"),
    path("rencana/daftar/", view_rencana.list, name="rencana_gajiasn_list"),
    path("rencana/filter/", view_rencana.filter, name="rencana_gajiasn_filter"),
    path("rencana/", view_rencana.home, name="rencana_gajiasn_home"),

    # Rencana Sisa
    path("rencanasisa/cetak", view_rencanasisa.cetak, name="rencana_gajiasn_cetaksisa"),
    path("rencanasisa/excel/", view_rencanasisa.excel, name="rencana_gajiasn_excelsisa"),
    path("rencanasisa/delete/<int:pk>/", view_rencanasisa.delete, name="rencana_gajiasn_deletesisa"),
    path("rencanasisa/update/<int:pk>/", view_rencanasisa.update, name="rencana_gajiasn_updatesisa"),
    path("rencanasisa/simpan/", view_rencanasisa.simpan, name="rencana_gajiasn_simpansisa"),
    path("rencanasisa/daftar/", view_rencanasisa.list, name="rencana_gajiasn_listsisa"),
    path("rencanasisa/filter/", view_rencanasisa.filter, name="rencana_gajiasn_filtersisa"),
]
