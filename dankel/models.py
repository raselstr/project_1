from django.db import models
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
from opd.models import Subopd
from dana.models import Subrinc
from dausg.models import Dankelsub
from datetime import datetime

# Create your models here.
class RencDankel(models.Model):
    VERIF = [
        (0, 'Input Dinas'),
        (1, 'Disetujui'),
        (2, 'Ditolak')
    ]
    rencdankel_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    rencdankel_dana = models.ForeignKey(Subrinc, verbose_name='Sumber Dana',on_delete=models.CASCADE,editable=False)
    rencdankel_subopd = models.ForeignKey(Subopd, verbose_name='Sub Opd',on_delete=models.CASCADE)
    rencdankel_sub = models.ForeignKey(Dankelsub, verbose_name='Sub Kegiatan', on_delete=models.CASCADE)
    rencdankel_pagu = models.DecimalField(verbose_name='Pagu Anggaran',max_digits=17, decimal_places=2,default=0)
    rencdankel_output = models.DecimalField(verbose_name='Output',max_digits=8, decimal_places=2,default=0)
    rencdankel_ket = models.TextField(verbose_name='Keterangan Kegiatan', blank=True)
    rencdankel_verif = models.IntegerField(choices=VERIF, default = 0, editable=False)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['rencdankel_tahun', 'rencdankel_subopd', 'rencdankel_sub'], name='unique_rencdankel')
        ]
    
    def clean(self):
        # Check if the combination already exists
        if RencDankel.objects.filter(
            rencdankel_tahun=self.rencdankel_tahun,
            rencdankel_subopd=self.rencdankel_subopd,
            rencdankel_sub=self.rencdankel_sub
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Rencana Kegiatan untuk Tahun, Sub Opd dan Sub Kegiatan ini sudah ada, silahkan masukkan yang lain.')
    
    def save(self, *args, **kwargs):
        # Set default value for rencdankel_dana if not provided
        if not self.rencdankel_dana_id:
            try:
                self.rencdankel_dana = Subrinc.objects.get(subrinc_slug='dana-kelurahan')
            except Subrinc.DoesNotExist:
                raise ValidationError('Sumber Dana dengan slug "dana-kelurahan" tidak ditemukan.')
        super(RencDankel, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.rencdankel_ket

class RencDankelsisa(models.Model):
    VERIF = [
        (0, 'Input Dinas'),
        (1, 'Disetujui'),
        (2, 'Ditolak')
    ]
    rencdankelsisa_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    rencdankelsisa_dana = models.ForeignKey(Subrinc, verbose_name='Sumber Dana',on_delete=models.CASCADE,editable=False)
    rencdankelsisa_subopd = models.ForeignKey(Subopd, verbose_name='Sub Opd',on_delete=models.CASCADE)
    rencdankelsisa_sub = models.ForeignKey(Dankelsub, verbose_name='Sub Kegiatan', on_delete=models.CASCADE)
    rencdankelsisa_pagu = models.DecimalField(verbose_name='Pagu Anggaran Sisa',max_digits=17, decimal_places=2,default=0, blank=True)
    rencdankelsisa_output = models.DecimalField(verbose_name='Output Sisa',max_digits=8, decimal_places=2,default=0, blank=True)
    rencdankelsisa_ket = models.TextField(verbose_name='Keterangan Kegiatan Sisa', blank=True)
    rencdankelsisa_verif = models.IntegerField(choices=VERIF, default = 0, editable=False) 
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['rencdankelsisa_tahun', 'rencdankelsisa_subopd', 'rencdankelsisa_sub'], name='unique_rencdankelsisa')
        ]
    
    def clean(self):
        # Check if the combination already exists
        if RencDankelsisa.objects.filter(
            rencdankelsisa_tahun=self.rencdankelsisa_tahun,
            rencdankelsisa_subopd=self.rencdankelsisa_subopd,
            rencdankelsisa_sub=self.rencdankelsisa_sub
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Rencana Kegiatan untuk Tahun, Sub Opd dan Sub Kegiatan ini sudah ada, silahkan masukkan yang lain.')
    
    def save(self, *args, **kwargs):
        # Set default value for rencdankel_dana if not provided
        if not self.rencdankelsisa_dana_id:
            try:
                self.rencdankelsisa_dana = Subrinc.objects.get(subrinc_slug='dana-kelurahan')
            except Subrinc.DoesNotExist:
                raise ValidationError('Sumber Dana dengan slug "dana-kelurahan" tidak ditemukan.')
        super(RencDankelsisa, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.rencdankelsisa_ket