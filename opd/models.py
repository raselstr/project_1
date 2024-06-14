from django.db import models
from project.validations import *

class Opd(models.Model):
    kode_opd = models.CharField(
        verbose_name="Kode OPD",
        max_length=10,
        unique=True,
        error_messages={'unique': 'Data, nilai ini sudah ada dalam database.'},
        validators=[
            number_validator,
            # partial(unik, app_name='opd', model_name='Opd', field='kode_opd')
            ]
        )
    
    nama_opd = models.CharField(
        verbose_name="Nama OPD",
        max_length=100,
        unique=True,
        error_messages={'unique': 'Maaf, nilai ini sudah ada dalam database.'},
        validators=[
            minimal2_validator,
            
            ]
        )

    def __str__(self):
        return self.nama_opd

class SubOpd(models.Model):
    sub_opd = models.ForeignKey(Opd, verbose_name='Opd', on_delete=models.CASCADE)
    sub_nama = models.CharField(verbose_name='Nama Sub Opd', max_length=200)
    
    def __str__(self):
        return self.sub_nama