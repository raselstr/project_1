from django.db import models

class Opd(models.Model):
    kode_opd = models.CharField(max_length=10)
    nama_opd = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_opd

    def simpan_opd(self):
        self.save()
