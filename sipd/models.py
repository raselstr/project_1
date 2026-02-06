from django.db import models

class Sipd(models.Model):
    tahun = models.IntegerField()
    # ===== Identitas Organisasi =====
    kode_sub_skpd = models.CharField(max_length=50)
    nama_sub_skpd = models.CharField(max_length=255)

    # ===== Program & Kegiatan =====
    kode_program = models.CharField(max_length=50)
    nama_program = models.CharField(max_length=255)

    kode_kegiatan = models.CharField(max_length=50)
    nama_kegiatan = models.CharField(max_length=255)

    kode_sub_kegiatan = models.CharField(max_length=50)
    nama_sub_kegiatan = models.CharField(max_length=255)

    # ===== Rekening =====
    kode_rekening = models.CharField(max_length=50)
    nama_rekening = models.CharField(max_length=255)

    # ===== Dokumen =====
    nomor_dokumen = models.CharField(max_length=100, blank=True, null=True)
    jenis_dokumen = models.CharField(max_length=50, blank=True, null=True)
    jenis_transaksi = models.CharField(max_length=50, blank=True, null=True)
    nomor_dpt = models.CharField(max_length=100, blank=True, null=True)

    tanggal_dokumen = models.DateField(blank=True, null=True)
    keterangan_dokumen = models.TextField(blank=True, null=True)

    # ===== Nilai =====
    nilai_realisasi = models.DecimalField(
        max_digits=20, decimal_places=2, default=0
    )
    nilai_setoran = models.DecimalField(
        max_digits=20, decimal_places=2, default=0
    )

    # ===== SPP =====
    nomor_spp = models.CharField(max_length=100, blank=True, null=True)
    tanggal_spp = models.DateField(blank=True, null=True)

    # ===== SPM =====
    nomor_spm = models.CharField(max_length=100, blank=True, null=True)
    tanggal_spm = models.DateField(blank=True, null=True)

    # ===== SP2D =====
    nomor_sp2d = models.CharField(max_length=100, blank=True, null=True)
    tanggal_sp2d = models.DateField(blank=True, null=True)
    tanggal_transfer = models.DateField(blank=True, null=True)

    nilai_sp2d = models.DecimalField(
        max_digits=20, decimal_places=2, default=0
    )

    # ===== Metadata =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sipd"
        verbose_name = "Realisasi SIPD"
        verbose_name_plural = "Realisasi SIPD"

        # 🔐 Anti duplikasi (umum di SIPD)
        unique_together = (
            'tahun',
            'kode_sub_skpd',
            'kode_sub_kegiatan',
            'kode_rekening',
            'nomor_dokumen',
            'nomor_spm',
            'nomor_sp2d',
        )

    def __str__(self):
        return f"{self.kode_sub_skpd} - {self.kode_sub_kegiatan} - {self.kode_rekening} - {self.nomor_dokumen}"

