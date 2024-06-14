from django.db import models
from opd.models import Opd
from dausg.models import Dankelsub
from datetime import datetime

# Create your models here.
class RencDankel(models.Model):
    rencdankel_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    rencdankel_opd = models.ForeignKey(Opd, verbose_name='Opd',on_delete=models.CASCADE)
    rencdankel_sub = models.ForeignKey(Dankelsub, verbose_name='Sub Kegiatan', on_delete=models.CASCADE)
    rencdankel_pagu = models.DecimalField(verbose_name='Pagu Anggaran',max_digits=17, decimal_places=2,default=0)
    rencdankel_output = models.DecimalField(verbose_name='Output',max_digits=8, decimal_places=2,default=0)
    rencdankel_ket = models.TextField(verbose_name='Keterangan Kegiatan', blank=True) 
    
    def __str__(self):
        return self.rencdankel_ket

class RencDankelsisa(models.Model):
    rencdankelsisa_rencana = models.OneToOneField(RencDankel, verbose_name='Rencana Kegiatan', on_delete=models.CASCADE, related_name='rencdankelsisa')
    rencdankelsisa_pagu = models.DecimalField(verbose_name='Pagu Anggaran Sisa',max_digits=17, decimal_places=2,default=0, blank=True)
    rencdankelsisa_output = models.DecimalField(verbose_name='Output Sisa',max_digits=8, decimal_places=2,default=0, blank=True)
    rencdankelsisa_ket = models.TextField(verbose_name='Keterangan Kegiatan Sisa', blank=True) 
    
    def __str__(self):
        return self.rencdankelsisa_ket