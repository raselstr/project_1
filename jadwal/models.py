from django.db import models, transaction
from django.core.exceptions import ValidationError


class Jadwal(models.Model):
    jadwal_tahun = models.IntegerField(verbose_name="Tahun")
    jadwal_keterangan = models.CharField(verbose_name="Keterangan", max_length=200)
    jadwal_aktif = models.BooleanField(verbose_name="Aktif", default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["jadwal_tahun"],
                condition=models.Q(jadwal_aktif=True),
                name="unique_active_jadwal_per_tahun",
            )
        ]
        indexes = [
            models.Index(fields=["jadwal_tahun", "jadwal_aktif"]),
        ]

    def __str__(self):
        return f"{self.jadwal_keterangan} - {self.jadwal_tahun}"

    # ======================================================
    # AKTIFKAN JADWAL DENGAN AMAN
    # ======================================================
    def activate(self):
        """
        Mengaktifkan jadwal ini dan menonaktifkan
        semua jadwal lain di tahun yang sama.
        """
        with transaction.atomic():
            # nonaktifkan jadwal lain di tahun sama
            Jadwal.objects.filter(
                jadwal_tahun=self.jadwal_tahun,
                jadwal_aktif=True,
            ).exclude(pk=self.pk).update(jadwal_aktif=False)

            # aktifkan yang ini
            self.jadwal_aktif = True
            self.save(update_fields=["jadwal_aktif"])
