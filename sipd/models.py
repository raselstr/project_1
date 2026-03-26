from django.db import models
from django.db.models import Q

class Sipd(models.Model):
    tahun = models.IntegerField()

    # ===== Identitas =====
    kode_sub_skpd = models.CharField(max_length=50)
    nama_sub_skpd = models.CharField(max_length=255)

    # ===== Program =====
    kode_program = models.CharField(max_length=50)
    nama_program = models.TextField(blank=True, null=True)

    kode_kegiatan = models.CharField(max_length=50)
    nama_kegiatan = models.TextField(blank=True, null=True)

    kode_sub_kegiatan = models.CharField(max_length=50)
    nama_sub_kegiatan = models.TextField(blank=True, null=True)

    # ===== Rekening =====
    kode_rekening = models.CharField(max_length=50)
    nama_rekening = models.TextField(blank=True, null=True)

    # ===== DOKUMEN (🔥 FIX DI SINI)
    nomor_dokumen = models.CharField(max_length=100, blank=True, default="")
    nomor_spm = models.CharField(max_length=100, blank=True, default="")
    nomor_sp2d = models.CharField(max_length=100, blank=True, default="")

    jenis_dokumen = models.CharField(max_length=50, blank=True, null=True)
    jenis_transaksi = models.CharField(max_length=50, blank=True, null=True)
    nomor_dpt = models.CharField(max_length=100, blank=True, null=True)

    tanggal_dokumen = models.DateField(blank=True, null=True)
    keterangan_dokumen = models.TextField(blank=True, null=True)

    # ===== NILAI =====
    nilai_realisasi = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    nilai_setoran = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    # ===== SPP =====
    nomor_spp = models.CharField(max_length=100, blank=True, null=True)
    tanggal_spp = models.DateField(blank=True, null=True)

    # ===== SPM =====
    tanggal_spm = models.DateField(blank=True, null=True)

    # ===== SP2D =====
    tanggal_sp2d = models.DateField(blank=True, null=True)
    tanggal_transfer = models.DateField(blank=True, null=True)

    nilai_sp2d = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sipd"

        # 🔐 UNIQUE FINAL (ANTI DUPLIKAT)
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tahun",
                    "kode_sub_skpd",
                    "kode_sub_kegiatan",
                    "kode_rekening",
                    "nomor_dokumen",
                    "nomor_spm",
                    "nomor_sp2d",
                ],
                name="unique_sipd_data"
            ),

            # 🔒 LARANG KOSONG
            models.CheckConstraint(
                condition=(
                    ~Q(nomor_dokumen="") &
                    ~Q(nomor_spm="") &
                    ~Q(nomor_sp2d="")
                ),
                name="no_empty_unique_fields"
            )
        ]

    def __str__(self):
        return f"{self.kode_sub_skpd} - {self.kode_sub_kegiatan} - {self.kode_rekening} - {self.nomor_dokumen}"


class TBP(models.Model):
    tahun = models.IntegerField()

    tanggal_tbp = models.DateField(blank=True, null=True)

    nomor_tbp = models.CharField(
        max_length=100,
    )

    keterangan_tbp = models.TextField(blank=True, null=True)

    status_tbp = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    nilai_tbp = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tbp"
        ordering = ["-tanggal_tbp"]
        constraints = [
            models.UniqueConstraint(
                fields=["tahun", "nomor_tbp"],
                name="unique_tbp_per_tahun"
            )
        ]
        indexes = [
            models.Index(fields=["tahun"]),
            models.Index(fields=["nomor_tbp"]),
        ]

    def __str__(self):
        return f"{self.nomor_tbp} - {self.tanggal_tbp}"