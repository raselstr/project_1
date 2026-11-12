from django.db import models


class RegisterSP2D(models.Model):
    """
    Model Register SP2D (Transaksi) – data diimport dari Excel SIPD laporan register SP2D.
    Kolom Excel:
        A: No.
        B: Tanggal SP2D (Pembuatan)
        C: Tanggal SP2D (Pencairan)
        D: Nomor SP2D
        E: Unit SKPD
        F: Nama Penerima
        G: Keterangan
        H: Jenis SP2D
        I: Nilai Bruto
        J: Nilai Potongan
        K: Nilai Neto
    """

    # ===== PERIODE / TAHUN =====
    tahun = models.IntegerField(verbose_name="Tahun")
    bulan = models.IntegerField(verbose_name="Bulan", null=True, blank=True)

    # ===== TANGGAL =====
    tanggal_pembuatan  = models.DateField(verbose_name="Tanggal Pembuatan SP2D",  null=True, blank=True)
    tanggal_pencairan  = models.DateField(verbose_name="Tanggal Pencairan SP2D",  null=True, blank=True)

    # ===== NOMOR & IDENTITAS =====
    nomor_sp2d   = models.CharField(max_length=150, verbose_name="Nomor SP2D")
    unit_skpd    = models.TextField(verbose_name="Unit SKPD", blank=True, null=True)
    nama_penerima = models.TextField(verbose_name="Nama Penerima", blank=True, null=True)
    keterangan   = models.TextField(verbose_name="Keterangan",    blank=True, null=True)
    jenis_sp2d   = models.CharField(max_length=20, verbose_name="Jenis SP2D", blank=True, null=True)

    # ===== NILAI =====
    nilai_bruto   = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Nilai Bruto (Rp)")
    nilai_potongan = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Nilai Potongan (Rp)")
    nilai_neto    = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Nilai Neto (Rp)")

    # ===== AUDIT =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "register_sp2d"
        ordering = ["tanggal_pembuatan", "nomor_sp2d"]
        verbose_name = "Register SP2D"
        verbose_name_plural = "Register SP2D"
        constraints = [
            models.UniqueConstraint(
                fields=["tahun", "nomor_sp2d"],
                name="unique_register_sp2d_per_tahun"
            )
        ]
        indexes = [
            models.Index(fields=["tahun"]),
            models.Index(fields=["nomor_sp2d"]),
            models.Index(fields=["jenis_sp2d"]),
            models.Index(fields=["tanggal_pembuatan"]),
        ]

    def __str__(self):
        return f"{self.nomor_sp2d} ({self.tahun})"
