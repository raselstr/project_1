from django.contrib import admin
from .models import RegisterSP2D


@admin.register(RegisterSP2D)
class RegisterSP2DAdmin(admin.ModelAdmin):
    list_display = (
        "tahun", "tanggal_pembuatan", "nomor_sp2d",
        "unit_skpd", "jenis_sp2d", "nilai_bruto", "nilai_neto"
    )
    list_filter  = ("tahun", "jenis_sp2d", "bulan")
    search_fields = ("nomor_sp2d", "unit_skpd", "nama_penerima")
    ordering = ("tanggal_pembuatan", "nomor_sp2d")
