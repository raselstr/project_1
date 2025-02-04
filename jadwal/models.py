from django.db import models

# Create your models here.
class Jadwal(models.Model):
    jadwal_tahun = models.IntegerField(verbose_name="Tahun")
    jadwal_keterangan = models.CharField(verbose_name="Keterangan", max_length=200)
    jadwal_aktif = models.BooleanField(verbose_name="Aktif", default=True)

    def __str__(self):
        return f"{self.jadwal_keterangan} - {self.jadwal_tahun}"
