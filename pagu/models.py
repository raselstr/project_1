from django.db import models
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
from django.db.models import Sum
from opd.models import Subopd
from dana.models import Subkegiatan
from datetime import datetime


class Pagudausg(models.Model):
    pagudausg_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)    
    pagudausg_opd = models.ForeignKey(Subopd, verbose_name='Sub OPD', on_delete=models.CASCADE)
    pagudausg_dana = models.ForeignKey(Subkegiatan, verbose_name='Dana', on_delete=models.CASCADE)
    pagudausg_nilai = models.DecimalField(verbose_name='Pagu Anggaran', max_digits=17,decimal_places=2, default=0)
    pagudausg_sisa = models.DecimalField(verbose_name='Pagu Sisa Anggaran', max_digits=17,decimal_places=2, default=0)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['pagudausg_tahun', 'pagudausg_opd', 'pagudausg_dana'], name='unique_pagudausg')
        ]
        
    def clean(self):
        # Check if the combination already exists
        if Pagudausg.objects.filter(
            pagudausg_tahun=self.pagudausg_tahun,
            pagudausg_opd=self.pagudausg_opd,
            pagudausg_dana=self.pagudausg_dana
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Rencana Kegiatan untuk Tahun, Opd dan Dana ini sudah ada, silahkan masukkan yang lain.')
    
    def __str__(self):
        return f"{self.pagudausg_opd.sub_nama}"
    
    def total_nilai_by_dana(self, tahun=None):
        queryset = Pagudausg.objects.select_related('pagudausg_dana').values('pagudausg_dana__sub_nama')
        
        # Filter data berdasarkan tahun jika diberikan
        if tahun:
            queryset = queryset.filter(pagudausg_tahun=tahun)

        # Hitung total nilai dan sisa
        result = queryset.annotate(
            total_nilai=Sum('pagudausg_nilai'),
            total_sisa=Sum('pagudausg_sisa')
        ).order_by('pagudausg_dana__sub_nama')
        
        return result
    
