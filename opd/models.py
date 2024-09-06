from django.db import models
from project.validations import *
from dana.models import Subkegiatan

class Opd(models.Model):
    kode_opd = models.CharField(
        verbose_name="Kode OPD",
        max_length=25,
        unique=True,
        error_messages={'unique': 'Data, nilai ini sudah ada dalam database.'},
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

class Subopd(models.Model):
    sub_opd = models.ForeignKey(Opd, verbose_name='Sub Opd', on_delete=models.CASCADE)
    sub_nama = models.CharField(verbose_name='Nama Sub Opd', max_length=200)
    
    def __str__(self):
        return self.sub_nama


class Pejabat(models.Model):
    pejabat_sub = models.OneToOneField(Subopd, verbose_name='Nama OPD', on_delete=models.CASCADE, unique=True, error_messages='OPD ini sudah memiliki Pejabat')
    pejabat_jabatan = models.CharField(verbose_name='Jabatan', max_length=40)
    pejabat_nama = models.CharField(verbose_name='Nama Pejabat', max_length=40)
    pejabat_nip = models.CharField(verbose_name='NIP', max_length=18, unique=True, error_messages='NIP sudah ada')
    pejabat_lokasi = models.CharField(verbose_name='Nama Lokasi', max_length=50)
    pejabat_foto = models.ImageField(upload_to='kop_fotos/', verbose_name='Foto Pejabat', blank=True, null=True)
    
    def __str__(self):
        return self.pejabat_nama

class OpdDana(models.Model):
    opddana_dana = models.ForeignKey(Subkegiatan, verbose_name='Dana', on_delete=models.CASCADE)
    opddana_subopd = models.ForeignKey(Subopd, verbose_name='OPD Pengelola', on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.opddana_dana}' 
    