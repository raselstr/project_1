from django.db import models
from django.core import validators

class Opd(models.Model):
    kode_opd = models.CharField(
        max_length=10,
        unique=True,
        validators=[validators.RegexValidator(regex='^[0-9]+$', message='Kode OPD harus berupa angka')]
        )
    nama_opd = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_opd

    