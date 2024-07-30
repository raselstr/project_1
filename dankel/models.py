from django.db import models
from django.db.models import Sum, Q
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
from opd.models import Subopd
from dana.models import Subkegiatan, TahapDana
from dausg.models import Dankelsub
from pagu.models import Pagudausg
from penerimaan.models import Penerimaan, DistribusiPenerimaan
from datetime import datetime

from decimal import Decimal

# Create your models here.
VERIF = [
        (0, 'Input Dinas'),
        (1, 'Disetujui'),
        (2, 'Ditolak')
    ]

class RencDankel(models.Model):
    
    rencdankel_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    rencdankel_dana = models.ForeignKey(Subkegiatan, verbose_name='Sumber Dana',on_delete=models.CASCADE)
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
        
        # Check if the total planned budget does not exceed the available budget
        total_rencana = self.get_total_rencana(self.rencdankel_tahun, self.rencdankel_subopd, self.rencdankel_dana)
        total_pagudausg = self.get_pagudausg(self.rencdankel_tahun, self.rencdankel_subopd, self.rencdankel_dana)
        
        # Include the current instance's budget in the total_rencana
        if self.pk:
            total_rencana = total_rencana - RencDankel.objects.get(pk=self.pk).rencdankel_pagu

        total_rencana += self.rencdankel_pagu
        
        if total_rencana > total_pagudausg:
            raise ValidationError('Total rencana anggaran tidak boleh lebih besar dari total anggaran yang tersedia.')
            
    def save(self, *args, **kwargs):
        super(RencDankel, self).save(*args, **kwargs)
    
    def get_pagudausg(self, tahun, opd, dana):
        filters = Q(pagudausg_tahun=tahun) & Q(pagudausg_dana=dana)
        if opd is not None:
            filters &= Q(pagudausg_opd=opd)
        return Pagudausg.objects.filter(filters).aggregate(total_nilai=Sum('pagudausg_nilai'))['total_nilai'] or Decimal(0)
    
    def get_total_rencana(self, tahun, opd, dana):
        filters = Q(rencdankel_tahun=tahun) & Q(rencdankel_dana=dana)
        if opd is not None:
            filters &= Q(rencdankel_subopd=opd)
        return RencDankel.objects.filter(filters).aggregate(total_nilai=Sum('rencdankel_pagu'))['total_nilai'] or Decimal(0)
       
    def sisa(self, tahun, opd, dana):
        total_rencana = self.get_total_rencana(tahun, opd, dana)
        total_pagudausg = self.get_pagudausg(tahun, opd, dana)
        return total_pagudausg - total_rencana

    def __str__(self):
        return f"{self.rencdankel_sub}"

class RencDankelsisa(models.Model):
    
    rencdankelsisa_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    rencdankelsisa_dana = models.ForeignKey(Subkegiatan, verbose_name='Sumber Dana',on_delete=models.CASCADE)
    rencdankelsisa_subopd = models.ForeignKey(Subopd, verbose_name='Sub Opd',on_delete=models.CASCADE)
    rencdankelsisa_sub = models.ForeignKey(Dankelsub, verbose_name='Sub Kegiatan', on_delete=models.CASCADE)
    rencdankelsisa_pagu = models.DecimalField(verbose_name='Pagu Anggaran Sisa',max_digits=17, decimal_places=2,default=0)
    rencdankelsisa_output = models.DecimalField(verbose_name='Output Sisa',max_digits=8, decimal_places=2,default=0)
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
        
        # Check if the total planned budget does not exceed the available budget
        total_rencana = self.get_total_sisa(self.rencdankelsisa_tahun, self.rencdankelsisa_subopd, self.rencdankelsisa_dana)
        total_pagudausg = self.get_sisapagudausg(self.rencdankelsisa_tahun, self.rencdankelsisa_subopd, self.rencdankelsisa_dana)
        
        # Include the current instance's budget in the total_rencana
        if self.pk:
            total_rencana = total_rencana - RencDankelsisa.objects.get(pk=self.pk).rencdankelsisa_pagu

        total_rencana += self.rencdankelsisa_pagu
        
        if total_rencana > total_pagudausg:
            raise ValidationError('Total rencana anggaran tidak boleh lebih besar dari total anggaran yang tersedia.')
    
    def save(self, *args, **kwargs):
        super(RencDankelsisa, self).save(*args, **kwargs)
    
    def get_sisapagudausg(self, tahun, opd, dana):
        filters = Q(pagudausg_tahun=tahun) & Q(pagudausg_dana=dana)
        if opd is not None:
            filters &= Q(pagudausg_opd=opd)
        return Pagudausg.objects.filter(filters).aggregate(total_nilai=Sum('pagudausg_sisa'))['total_nilai'] or Decimal(0)
    
    def get_total_sisa(self, tahun, opd, dana):
        filters = Q(rencdankelsisa_tahun=tahun) & Q(rencdankelsisa_dana=dana)
        if opd is not None:
            filters &= Q(rencdankelsisa_subopd=opd)
        return RencDankelsisa.objects.filter(filters).aggregate(total_nilai=Sum('rencdankelsisa_pagu'))['total_nilai'] or Decimal(0)
       
    def sisa_sisa(self, tahun, opd, dana):
        total_sisarencana = self.get_total_sisa(tahun, opd, dana)
        total_pagudausg = self.get_sisapagudausg(tahun, opd, dana)
        return total_pagudausg - total_sisarencana 
    
    def __str__(self):
        return self.rencdankelsisa_ket
    
    
class RealisasiDankel(models.Model):
    
    realisasidankel_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    realisasidankel_dana = models.ForeignKey(Subkegiatan, verbose_name='Sumber Dana',on_delete=models.CASCADE)
    realisasidankel_tahap = models.ForeignKey(TahapDana, verbose_name='Tahap Realisasi',on_delete=models.CASCADE)
    realisasidankel_subopd = models.ForeignKey(Subopd, verbose_name='Sub Opd',on_delete=models.CASCADE)
    realisasidankel_rencana = models.ForeignKey(RencDankel, verbose_name='Kegiatan', on_delete=models.CASCADE)
    realisasidankel_sp2dtu = models.CharField(verbose_name='No SP2D TU', max_length=100, unique=True)
    realisasidankel_tgl = models.DateField(verbose_name='Tanggal SP2D TU')
    realisasidankel_nilai = models.DecimalField(verbose_name='Nilai SP2D', max_digits=17, decimal_places=2,default=0)
    realisasidankel_lpj = models.CharField(verbose_name='No LPJ TU', max_length=100, unique=True)
    realisasidankel_lpjtgl = models.DateField(verbose_name='Tanggal LPJ TU')
    realisasidankel_lpjnilai = models.DecimalField(verbose_name='Nilai LPJ TU', max_digits=17, decimal_places=2,default=0)
    realisasidankel_sts = models.CharField(verbose_name='No STS TU', max_length=100, unique=True)
    realisasidankel_ststgl = models.DateField(verbose_name='Tanggal STS TU')
    realisasidankel_stsnilai = models.DecimalField(verbose_name='Nilai STS TU', max_digits=17, decimal_places=2,default=0)
    realisasidankel_verif = models.IntegerField(choices=VERIF, default = 0, editable=False) 
    
    def clean(self):
        total_penerimaan = self.get_penerimaan_total(self.realisasidankel_tahun, self.realisasidankel_subopd_id, self.realisasidankel_dana_id)
        total_realisasi = self.get_realisasilpj_total(self.realisasidankel_tahun, self.realisasidankel_subopd_id, self.realisasidankel_dana_id)
        
        if self.pk:
            total_realisasi = total_realisasi - RealisasiDankel.objects.get(pk=self.pk).realisasidankel_lpjnilai

        total_realisasi += self.realisasidankel_lpjnilai
        
        if total_realisasi > total_penerimaan:
            raise ValidationError('Total Realisasi LPJ tidak boleh lebih besar dari total Penerimaan yang tersedia.')
        
    def save(self, *args, **kwargs):
        super(RealisasiDankel, self).save(*args, **kwargs)
        
    
    def get_penerimaan_total(self, tahun, opd, dana):
        filters = Q(distri_penerimaan__penerimaan_tahun=tahun) & Q(distri_penerimaan__penerimaan_dana=dana)
        if opd is not None:
            filters &= Q(distri_subopd=opd)
        return DistribusiPenerimaan.objects.filter(filters).aggregate(total_nilai=Sum('distri_nilai'))['total_nilai'] or Decimal(0)
    
    def get_realisasilpj_total(self, tahun, opd, dana):
        filters = Q(realisasidankel_tahun=tahun) & Q(realisasidankel_dana=dana)
        if opd is not None:
            filters &= Q(realisasidankel_subopd=opd)
        return RealisasiDankel.objects.filter(filters).aggregate(total_nilai=Sum('realisasidankel_lpjnilai'))['total_nilai'] or Decimal(0)
    
    def get_persentase(self, tahun, opd, dana):
        lpj = self.get_realisasilpj_total(tahun, opd, dana)
        penerimaan = self.get_penerimaan_total(tahun, opd, dana)
        return ((lpj/penerimaan)*100)
    
    def get_rencana_pk(self, tahun, opd, dana, pk):
        filters = Q(realisasidankel_tahun=tahun) & Q(realisasidankel_dana=dana)
        if opd is not None:
            filters &= Q(realisasidankel_subopd=opd) & Q(realisasidankel_rencana=pk)
        return RealisasiDankel.objects.filter(filters).aggregate(total_nilai=Sum('realisasidankel_lpjnilai'))['total_nilai'] or Decimal(0)
    
    def __str__(self):
        return f'{self.realisasidankel_dana}-{self.realisasidankel_tahap}'

