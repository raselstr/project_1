from django.db import models
from django.db.models import Sum, Q
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
from opd.models import Subopd
from dana.models import Subkegiatan, TahapDana
from dausg.models import Dankelsub
from pagu.models import Pagudausg
from penerimaan.models import DistribusiPenerimaan
from datetime import datetime
from jadwal.models import Jadwal
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
        total_realisasi_pk = self.get_realisasi_pk()
        
        
        # Include the current instance's budget in the total_rencana
        if self.pk:
            total_rencana = total_rencana - RencDankel.objects.get(pk=self.pk).rencdankel_pagu

        total_rencana += self.rencdankel_pagu
        
        formatted_total_realisasi_pk = "{:,.2f}".format(total_realisasi_pk)
        
        if self.rencdankel_pagu < total_realisasi_pk :
            raise ValidationError(f'Kegiatan ini sudah ada realisasi sebesar Rp. {formatted_total_realisasi_pk} Nilai Rencana tidak boleh lebih kecil dari Nilai Realisasi')
        
        if total_rencana > total_pagudausg:
            raise ValidationError('Total rencana anggaran tidak boleh lebih besar dari total anggaran yang tersedia.')
            
    def save(self, *args, **kwargs):
        super(RencDankel, self).save(*args, **kwargs)
    
    def get_pagudausg(self, tahun, opd, dana):
        filters = Q(pagudausg_tahun=tahun) & Q(pagudausg_dana=dana)
        if opd is not None and opd !=124 and opd != 70 and opd !=67:
            filters &= Q(pagudausg_opd=opd)
        return Pagudausg.objects.filter(filters).aggregate(total_nilai=Sum('pagudausg_nilai'))['total_nilai'] or Decimal(0)
    
    def get_total_rencana(self, tahun, opd, dana):
        filters = Q(rencdankel_tahun=tahun) & Q(rencdankel_dana=dana)
        if opd is not None and opd !=124 and opd != 70 and opd !=67:
            filters &= Q(rencdankel_subopd=opd)
        return RencDankel.objects.filter(filters).aggregate(total_nilai=Sum('rencdankel_pagu'))['total_nilai'] or Decimal(0)
       
    def sisa(self, tahun, opd, dana):
        total_rencana = self.get_total_rencana(tahun, opd, dana)
        total_pagudausg = self.get_pagudausg(tahun, opd, dana)
        return total_pagudausg - total_rencana
    
  
    def get_realisasi_pk(self):
        filters = Q(realisasidankel_tahun=self.rencdankel_tahun) & Q(realisasidankel_dana=self.rencdankel_dana_id) & Q(realisasidankel_idrencana_id = self.id)
        if self.rencdankel_subopd is not None:
            filters &= Q(realisasidankel_subopd=self.rencdankel_subopd_id)
        nilai_realisasi = RealisasiDankel.objects.filter(filters).aggregate(total_nilai=Sum('realisasidankel_lpjnilai'))['total_nilai'] or Decimal(0)
        # print(f"nilai realisasi : {nilai_realisasi} dan {filters}")
        return nilai_realisasi

    def get_satuan_kegiatan(self):
        return self.rencdankel_sub.dankelsub_satuan if self.rencdankel_sub else None
    
    def get_subkegiatan(self):
        return self.rencdankel_sub.dankelsub_nama if self.rencdankel_sub else None
    
    def get_kegiatan(self):
        return self.rencdankel_sub.dankelsub_keg.dankelkeg_nama if self.rencdankel_sub else None
    
    def get_program(self):
        return self.rencdankel_sub.dankelsub_keg.dankelkeg_prog.dankel_prog if self.rencdankel_sub else None
    
    def __str__(self):
        return str(self.rencdankel_sub)

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
        total_realisasi_pk = self.get_realisasi_pk()
        
        # Include the current instance's budget in the total_rencana
        if self.pk:
            total_rencana = total_rencana - RencDankelsisa.objects.get(pk=self.pk).rencdankelsisa_pagu

        total_rencana += self.rencdankelsisa_pagu
        
        formatted_total_realisasi_pk = "{:,.2f}".format(total_realisasi_pk)
        
        if self.rencdankelsisa_pagu < total_realisasi_pk :
            raise ValidationError(f'Kegiatan ini sudah ada realisasi sebesar Rp. {formatted_total_realisasi_pk} Nilai Rencana tidak boleh lebih kecil dari Nilai Realisasi')

        
        if total_rencana > total_pagudausg:
            raise ValidationError('Total rencana anggaran tidak boleh lebih besar dari total anggaran yang tersedia.')
    
    def save(self, *args, **kwargs):
        super(RencDankelsisa, self).save(*args, **kwargs)
    
    def get_sisapagudausg(self, tahun, opd, dana):
        filters = Q(pagudausg_tahun=tahun) & Q(pagudausg_dana=dana)
        if opd is not None and opd !=124 and opd != 70 and opd !=67:
            filters &= Q(pagudausg_opd=opd)
        return Pagudausg.objects.filter(filters).aggregate(total_nilai=Sum('pagudausg_nilai'))['total_nilai'] or Decimal(0)
    
    def get_total_sisa(self, tahun, opd, dana):
        filters = Q(rencdankelsisa_tahun=tahun) & Q(rencdankelsisa_dana=dana)
        if opd is not None and opd !=124 and opd != 70 and opd !=67:
            filters &= Q(rencdankelsisa_subopd=opd)
        return RencDankelsisa.objects.filter(filters).aggregate(total_nilai=Sum('rencdankelsisa_pagu'))['total_nilai'] or Decimal(0)
       
    def sisa_sisa(self, tahun, opd, dana):
        total_sisarencana = self.get_total_sisa(tahun, opd, dana)
        total_pagudausg = self.get_sisapagudausg(tahun, opd, dana)
        return total_pagudausg - total_sisarencana
    
    def get_realisasi_pk(self):
        filters = Q(realisasidankelsisa_tahun=self.rencdankelsisa_tahun) & Q(realisasidankelsisa_dana=self.rencdankelsisa_dana_id) & Q(realisasidankelsisa_idrencana_id = self.id)
        if self.rencdankelsisa_subopd is not None:
            filters &= Q(realisasidankelsisa_subopd=self.rencdankelsisa_subopd_id)
        nilai_realisasi = RealisasiDankelsisa.objects.filter(filters).aggregate(total_nilai=Sum('realisasidankelsisa_lpjnilai'))['total_nilai'] or Decimal(0)
        # print(f"nilai realisasi : {nilai_realisasi} dan {filters}")
        return nilai_realisasi
    
    def __str__(self):
        return f'{self.rencdankelsisa_sub}'
    
class RencDankeljadwal(models.Model):
    
    VERIF = [
        (1, 'Rencana Induk'),
        (2, 'Rencana Perubahan'),
    ]
    rencdankel_id = models.ForeignKey(RencDankel, verbose_name='Id Rencana', on_delete=models.CASCADE)
    rencdankel_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    rencdankel_dana = models.ForeignKey(Subkegiatan, verbose_name='Sumber Dana',on_delete=models.CASCADE)
    rencdankel_subopd = models.ForeignKey(Subopd, verbose_name='Sub Opd',on_delete=models.CASCADE)
    rencdankel_sub = models.ForeignKey(Dankelsub, verbose_name='Sub Kegiatan', on_delete=models.CASCADE)
    rencdankel_pagu = models.DecimalField(verbose_name='Pagu Anggaran',max_digits=17, decimal_places=2,default=0)
    rencdankel_output = models.DecimalField(verbose_name='Output',max_digits=8, decimal_places=2,default=0)
    rencdankel_ket = models.TextField(verbose_name='Keterangan Kegiatan', blank=True)
    rencdankel_jadwal = models.ForeignKey(Jadwal, verbose_name='Posting Jadwal', null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.rencdankel_sub}"

class RencDankeljadwalsisa(models.Model):
    
    VERIF = [
        (1, 'Rencana Induk'),
        (2, 'Rencana Perubahan'),
    ]
    
    rencdankelsisa_id = models.ForeignKey(RencDankelsisa, verbose_name='Id Rencana', on_delete=models.CASCADE)
    rencdankelsisa_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    rencdankelsisa_dana = models.ForeignKey(Subkegiatan, verbose_name='Sumber Dana',on_delete=models.CASCADE)
    rencdankelsisa_subopd = models.ForeignKey(Subopd, verbose_name='Sub Opd',on_delete=models.CASCADE)
    rencdankelsisa_sub = models.ForeignKey(Dankelsub, verbose_name='Sub Kegiatan', on_delete=models.CASCADE)
    rencdankelsisa_pagu = models.DecimalField(verbose_name='Pagu Anggaran Sisa',max_digits=17, decimal_places=2,default=0)
    rencdankelsisa_output = models.DecimalField(verbose_name='Output Sisa',max_digits=8, decimal_places=2,default=0)
    rencdankelsisa_ket = models.TextField(verbose_name='Keterangan Kegiatan Sisa', blank=True)
    rencdankelsisa_jadwal = models.ForeignKey(Jadwal, verbose_name='Posting Jadwal', null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.rencdankelsisa_sub}"
    

class RealisasiDankel(models.Model):
    
    realisasidankel_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    realisasidankel_dana = models.ForeignKey(Subkegiatan, verbose_name='Sumber Dana',on_delete=models.CASCADE)
    realisasidankel_tahap = models.ForeignKey(TahapDana, verbose_name='Tahap Realisasi',on_delete=models.CASCADE)
    realisasidankel_subopd = models.ForeignKey(Subopd, verbose_name='Sub Opd',on_delete=models.CASCADE)
    realisasidankel_rencana = models.ForeignKey(RencDankeljadwal, verbose_name='Kegiatan', on_delete=models.CASCADE)
    realisasidankel_idrencana = models.ForeignKey(RencDankel, verbose_name="Id Rencana", on_delete=models.CASCADE, editable=False)
    realisasidankel_output = models.IntegerField(verbose_name='Output')
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
        super().clean()
        
        total_penerimaan = self.get_penerimaan_total(self.realisasidankel_tahun, self.realisasidankel_subopd_id, self.realisasidankel_dana_id)
        total_realisasi = self.get_realisasilpj_total(self.realisasidankel_tahun, self.realisasidankel_subopd_id, self.realisasidankel_dana_id)
        total_rencana_pk = self.get_rencana_pk()
        total_realisasi_pk = self.get_realisasi_pk()
        total_rencanaoutput_pk = self.get_rencanaoutput_pk()
        
         
        
        if self.pk:
            total_realisasi_pk = total_realisasi_pk - RealisasiDankel.objects.get(pk=self.pk).realisasidankel_lpjnilai
            total_realisasi = total_realisasi - RealisasiDankel.objects.get(pk=self.pk).realisasidankel_lpjnilai
        
        total_realisasi_pk += self.realisasidankel_lpjnilai
        total_realisasi += self.realisasidankel_lpjnilai
        
        # Format nilai menjadi string dengan pemisah ribuan
        formatted_total_rencana_pk = "{:,.2f}".format(total_rencana_pk)
        formatted_total_realisasi_pk = "{:,.2f}".format(total_realisasi_pk)
        formatted_total_realisasi = "{:,.2f}".format(total_realisasi)
        formatted_total_penerimaan = "{:,.2f}".format(total_penerimaan)
        
        try:
            sp2dtu = Decimal(self.realisasidankel_nilai)
            lpj = Decimal(self.realisasidankel_lpjnilai)
            sts = Decimal(self.realisasidankel_stsnilai)
            output = Decimal(self.realisasidankel_output or 0)
            
        except ValueError:
            raise ValidationError('SP2D TU dan LPJ harus berupa angka.')
        
        if output > total_rencanaoutput_pk:
            raise ValidationError(f'Output tidak boleh lebih besar dari {total_rencanaoutput_pk}')
       
        if sp2dtu < 0:
            raise ValidationError('SP2D TU tidak boleh kurang dari 0')
    
        if lpj > sp2dtu:
            raise ValidationError('Nilai LPJ tidak boleh lebih besar dari SP2D TU')

        sisasts = sp2dtu - lpj

        if sts < 0:
            raise ValidationError('Nilai STS tidak boleh lebih kecil dari 0')

        if sts != sisasts:
            raise ValidationError(f'Nilai STS harus sama dengan {sisasts}')        

        
        if total_realisasi_pk > total_rencana_pk:
            raise ValidationError(f'Total Realisasi Kegiatan ini setelah ditambah nilai LPJ sekarang sebesar Rp. {formatted_total_realisasi_pk} tidak boleh lebih besar dari Rp. {formatted_total_rencana_pk} Nilai Rencana Kegiatan yang tersedia.')
        
        if total_realisasi > total_penerimaan:
            raise ValidationError(f'Total Realisasi Kegiatan Rp. {formatted_total_realisasi} tidak boleh lebih besar dari Rp. {formatted_total_penerimaan} Total Penerimaan yang tersedia.')
        
    def save(self, *args, **kwargs):
        self.full_clean()
        if self.realisasidankel_rencana:
            self.realisasidankel_idrencana = self.realisasidankel_rencana.rencdankel_id
        super().save(*args, **kwargs)

    def get_penerimaan_total(self, tahun, opd, dana):
        filters = Q(distri_penerimaan__penerimaan_tahun=tahun) & Q(distri_penerimaan__penerimaan_dana=dana)
        if opd is not None and opd != 124 and opd != 70 and opd !=67:
            filters &= Q(distri_subopd=opd)
        # print(filters)
        return DistribusiPenerimaan.objects.filter(filters).aggregate(total_nilai=Sum('distri_nilai'))['total_nilai'] or Decimal(0)

    def get_realisasilpj_total(self, tahun, opd, dana):
        filters = Q(realisasidankel_tahun=tahun) & Q(realisasidankel_dana=dana)
        if opd is not None and opd != 124 and opd != 70 and opd !=67:
            filters &= Q(realisasidankel_subopd=opd)
        return RealisasiDankel.objects.filter(filters).aggregate(total_nilai=Sum('realisasidankel_lpjnilai'))['total_nilai'] or Decimal(0)

    def get_persentase(self, tahun, opd, dana):
        try:
            lpj = self.get_realisasilpj_total(tahun, opd, dana)
            penerimaan = self.get_penerimaan_total(tahun, opd, dana)
            
            if lpj is None:
                return None
            if penerimaan is None:
                return 0
            return ((lpj / penerimaan) * 100)
        
        except ZeroDivisionError:
            return "Error: Pembagian tidak terdefinisi"  # Menangani pembagian dengan nol
        except Exception as e:
            return 0

    def get_rencana_pk(self):
        filters = Q(rencdankel_tahun=self.realisasidankel_tahun) & Q(rencdankel_dana_id=self.realisasidankel_dana_id)
        if self.realisasidankel_subopd_id is not None:
            filters &= Q(rencdankel_subopd_id=self.realisasidankel_subopd_id)
        if self.realisasidankel_rencana_id is not None:
            filters &= Q(id=self.realisasidankel_rencana_id)
        
        nilai_rencana = RencDankeljadwal.objects.filter(filters).aggregate(total_nilai=Sum('rencdankel_pagu'))['total_nilai'] or Decimal(0)
        # print(f"nilai rencana : {nilai_rencana} dan {filters}")
        return nilai_rencana
    
    def get_rencanaoutput_pk(self):
        filters = Q(rencdankel_tahun=self.realisasidankel_tahun) & Q(rencdankel_dana_id=self.realisasidankel_dana_id)
        if self.realisasidankel_subopd_id is not None:
            filters &= Q(rencdankel_subopd_id=self.realisasidankel_subopd_id)
        if self.realisasidankel_rencana_id is not None:
            filters &= Q(id=self.realisasidankel_rencana_id)
        
        nilai_output = RencDankeljadwal.objects.filter(filters).aggregate(total_nilai=Sum('rencdankel_output'))['total_nilai'] or Decimal(0)
        # print(f"nilai rencana : {nilai_rencana} dan {filters}")
        return nilai_output

    def get_realisasi_pk(self):
        filters = Q(realisasidankel_tahun=self.realisasidankel_tahun) & Q(realisasidankel_dana=self.realisasidankel_dana_id)
        if self.realisasidankel_rencana_id:
            realisasidankel_idrencana = self.realisasidankel_rencana.rencdankel_id
            filters &= Q(realisasidankel_idrencana = realisasidankel_idrencana)
            
        if self.realisasidankel_subopd_id is not None:
            filters &= Q(realisasidankel_subopd=self.realisasidankel_subopd_id)
        
        nilai_realisasi = RealisasiDankel.objects.filter(filters).aggregate(total_nilai=Sum('realisasidankel_lpjnilai'))['total_nilai'] or Decimal(0)
        # print(f"nilai realisasi : {nilai_realisasi} dan {filters}")
        return nilai_realisasi
        
    def __str__(self):
        return f'{self.realisasidankel_rencana}'

class RealisasiDankelsisa(models.Model):
    
    realisasidankelsisa_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    realisasidankelsisa_dana = models.ForeignKey(Subkegiatan, verbose_name='Sumber Dana',on_delete=models.CASCADE)
    realisasidankelsisa_tahap = models.ForeignKey(TahapDana, verbose_name='Tahap Realisasi',on_delete=models.CASCADE)
    realisasidankelsisa_subopd = models.ForeignKey(Subopd, verbose_name='Sub Opd',on_delete=models.CASCADE)
    realisasidankelsisa_rencana = models.ForeignKey(RencDankeljadwalsisa, verbose_name='Kegiatan', on_delete=models.CASCADE)
    realisasidankelsisa_idrencana = models.ForeignKey(RencDankelsisa, verbose_name="Id Rencana", on_delete=models.CASCADE, editable=False)
    realisasidankelsisa_output = models.IntegerField(verbose_name='Output')
    realisasidankelsisa_sp2dtu = models.CharField(verbose_name='No SP2D TU', max_length=100, unique=True)
    realisasidankelsisa_tgl = models.DateField(verbose_name='Tanggal SP2D TU')
    realisasidankelsisa_nilai = models.DecimalField(verbose_name='Nilai SP2D', max_digits=17, decimal_places=2,default=0)
    realisasidankelsisa_lpj = models.CharField(verbose_name='No LPJ TU', max_length=100, unique=True)
    realisasidankelsisa_lpjtgl = models.DateField(verbose_name='Tanggal LPJ TU')
    realisasidankelsisa_lpjnilai = models.DecimalField(verbose_name='Nilai LPJ TU', max_digits=17, decimal_places=2,default=0)
    realisasidankelsisa_sts = models.CharField(verbose_name='No STS TU', max_length=100, unique=True)
    realisasidankelsisa_ststgl = models.DateField(verbose_name='Tanggal STS TU')
    realisasidankelsisa_stsnilai = models.DecimalField(verbose_name='Nilai STS TU', max_digits=17, decimal_places=2,default=0)
    realisasidankelsisa_verif = models.IntegerField(choices=VERIF, default = 0, editable=False) 
    
    def clean(self):
        super().clean()
        
        total_penerimaan = self.get_penerimaan_total(self.realisasidankelsisa_tahun, self.realisasidankelsisa_subopd_id, self.realisasidankelsisa_dana_id)
        total_realisasi = self.get_realisasilpj_total(self.realisasidankelsisa_tahun, self.realisasidankelsisa_subopd_id, self.realisasidankelsisa_dana_id)
        total_rencana_pk = self.get_rencana_pk()
        total_realisasi_pk = self.get_realisasi_pk()
        total_rencanaoutputsisa_pk = self.get_rencanaoutputsisa_pk()
        
         
        
        if self.pk:
            total_realisasi_pk = total_realisasi_pk - RealisasiDankelsisa.objects.get(pk=self.pk).realisasidankelsisa_lpjnilai
            total_realisasi = total_realisasi - RealisasiDankelsisa.objects.get(pk=self.pk).realisasidankelsisa_lpjnilai
        
        total_realisasi_pk += self.realisasidankelsisa_lpjnilai
        total_realisasi += self.realisasidankelsisa_lpjnilai
        
        # Format nilai menjadi string dengan pemisah ribuan
        formatted_total_rencana_pk = "{:,.2f}".format(total_rencana_pk)
        formatted_total_realisasi_pk = "{:,.2f}".format(total_realisasi_pk)
        formatted_total_realisasi = "{:,.2f}".format(total_realisasi)
        formatted_total_penerimaan = "{:,.2f}".format(total_penerimaan)
        
        try:
            sp2dtu = Decimal(self.realisasidankelsisa_nilai)
            lpj = Decimal(self.realisasidankelsisa_lpjnilai)
            sts = Decimal(self.realisasidankelsisa_stsnilai)
            output = Decimal(self.realisasidankelsisa_output or 0)
            
        except ValueError:
            raise ValidationError('SP2D TU dan LPJ harus berupa angka.')
        
        if output > total_rencanaoutputsisa_pk:
            raise ValidationError(f'Output tidak boleh lebih besar dari {total_rencanaoutputsisa_pk}')
       
        if sp2dtu < 0:
            raise ValidationError('SP2D TU tidak boleh kurang dari 0')
    
        if lpj > sp2dtu:
            raise ValidationError('Nilai LPJ tidak boleh lebih besar dari SP2D TU')

        sisasts = sp2dtu - lpj

        if sts < 0:
            raise ValidationError('Nilai STS tidak boleh lebih kecil dari 0')

        if sts != sisasts:
            raise ValidationError(f'Nilai STS harus sama dengan {sisasts}')        

        
        if total_realisasi_pk > total_rencana_pk:
            raise ValidationError(f'Total Realisasi Kegiatan ini setelah ditambah nilai LPJ sekarang sebesar Rp. {formatted_total_realisasi_pk} tidak boleh lebih besar dari Rp. {formatted_total_rencana_pk} Nilai Rencana Kegiatan yang tersedia.')
        
        if total_realisasi > total_penerimaan:
            raise ValidationError(f'Total Realisasi Kegiatan Rp. {formatted_total_realisasi} tidak boleh lebih besar dari Rp. {formatted_total_penerimaan} Total Penerimaan yang tersedia.')
        
    def save(self, *args, **kwargs):
        self.full_clean()
        if self.realisasidankelsisa_rencana:
            self.realisasidankelsisa_idrencana = self.realisasidankelsisa_rencana.rencdankelsisa_id
        super().save(*args, **kwargs)

    def get_penerimaan_total(self, tahun, opd, dana):
        filters = Q(distri_penerimaan__penerimaan_tahun=tahun) & Q(distri_penerimaan__penerimaan_dana=dana)
        if opd is not None and opd != 124 and opd != 70 and opd !=67:
            filters &= Q(distri_subopd=opd)
        # print(filters)
        return DistribusiPenerimaan.objects.filter(filters).aggregate(total_nilai=Sum('distri_nilai'))['total_nilai'] or Decimal(0)

    def get_realisasilpj_total(self, tahun, opd, dana):
        filters = Q(realisasidankelsisa_tahun=tahun) & Q(realisasidankelsisa_dana=dana)
        if opd is not None and opd != 124 and opd != 70 and opd !=67:
            filters &= Q(realisasidankelsisa_subopd=opd)
        return RealisasiDankelsisa.objects.filter(filters).aggregate(total_nilai=Sum('realisasidankelsisa_lpjnilai'))['total_nilai'] or Decimal(0)

    def get_persentase(self, tahun, opd, dana):
        try:
            lpj = self.get_realisasilpj_total(tahun, opd, dana)
            penerimaan = self.get_penerimaan_total(tahun, opd, dana)
            
            if lpj is None:
                return None
            if penerimaan is None:
                return 0
            return ((lpj / penerimaan) * 100)
        
        except ZeroDivisionError:
            return "Error: Pembagian tidak terdefinisi"  # Menangani pembagian dengan nol
        except Exception as e:
            return 0

    def get_rencana_pk(self):
        filters = Q(rencdankelsisa_tahun=self.realisasidankelsisa_tahun) & Q(rencdankelsisa_dana_id=self.realisasidankelsisa_dana_id)
        if self.realisasidankelsisa_subopd_id is not None:
            filters &= Q(rencdankelsisa_subopd_id=self.realisasidankelsisa_subopd_id)
        if self.realisasidankelsisa_rencana_id is not None:
            filters &= Q(id=self.realisasidankelsisa_rencana_id)
        
        nilai_rencana = RencDankeljadwalsisa.objects.filter(filters).aggregate(total_nilai=Sum('rencdankelsisa_pagu'))['total_nilai'] or Decimal(0)
        # print(f"nilai rencana : {nilai_rencana} dan {filters}")
        return nilai_rencana
    
    def get_rencanaoutputsisa_pk(self):
        filters = Q(rencdankelsisa_tahun=self.realisasidankelsisa_tahun) & Q(rencdankelsisa_dana_id=self.realisasidankelsisa_dana_id)
        if self.realisasidankelsisa_subopd_id is not None:
            filters &= Q(rencdankelsisa_subopd_id=self.realisasidankelsisa_subopd_id)
        if self.realisasidankelsisa_rencana_id is not None:
            filters &= Q(id=self.realisasidankelsisa_rencana_id)
        
        nilai_outputsisa = RencDankeljadwalsisa.objects.filter(filters).aggregate(total_nilai=Sum('rencdankelsisa_output'))['total_nilai'] or Decimal(0)
        # print(f"nilai rencana : {nilai_rencana} dan {filters}")
        return nilai_outputsisa

    def get_realisasi_pk(self):
        filters = Q(realisasidankelsisa_tahun=self.realisasidankelsisa_tahun) & Q(realisasidankelsisa_dana=self.realisasidankelsisa_dana_id)
        if self.realisasidankelsisa_rencana_id:
            realisasidankelsisa_idrencana = self.realisasidankelsisa_rencana.rencdankelsisa_id
            filters &= Q(realisasidankelsisa_idrencana = realisasidankelsisa_idrencana)
            
        if self.realisasidankelsisa_subopd_id is not None:
            filters &= Q(realisasidankelsisa_subopd=self.realisasidankelsisa_subopd_id)
        
        nilai_realisasi = RealisasiDankelsisa.objects.filter(filters).aggregate(total_nilai=Sum('realisasidankelsisa_lpjnilai'))['total_nilai'] or Decimal(0)
        print(f"nilai realisasi : {nilai_realisasi} dan {filters}")
        return nilai_realisasi
        
    def __str__(self):
        return f'{self.realisasidankelsisa_rencana}'
    
