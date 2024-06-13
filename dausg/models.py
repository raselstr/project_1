from django.db import models
from dana.models import Subrinc, Dana

# Create your models here.
class DankelProg (models.Model):
    dankel_dana = models.ForeignKey(Dana, verbose_name="Dana", on_delete=models.CASCADE)
    dankel_subrinc = models.ForeignKey(Subrinc, verbose_name="Sub Rincian Dana", on_delete=models.CASCADE)
    dankel_prog = models.CharField(verbose_name="Program DAUSG", max_length=200)
    
    def __str__(self):
        return self.dankel_prog

class DankelKeg (models.Model):
    dankelkeg_prog = models.ForeignKey(DankelProg, verbose_name="Program DAUSG", on_delete=models.CASCADE, related_name='dankelkegs')
    dankelkeg_nama = models.CharField(verbose_name="Kegiatan DAUSG", max_length=200)
    
    def __str__(self):
        return self.dankelkeg_nama

class Dankelsub (models.Model):
    dankelsub_keg = models.ForeignKey(DankelKeg, verbose_name="Kegiatan DAUSG", on_delete=models.CASCADE, related_name='dankelsubs')
    dankelsub_nama = models.CharField(verbose_name="Sub Kegiatan DAUSG",max_length=200)
    dankelsub_satuan = models.CharField(verbose_name="Satuan",max_length=200)
    
    def __str__(self):
        return self.dankelsub_nama