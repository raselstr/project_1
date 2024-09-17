from django.db import models
from datetime import datetime
from django.db.models import Sum, Q
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
from decimal import Decimal

from opd.models import Subopd
from dana.models import Subkegiatan, TahapDana
from dausg.models import DausgpendidikanSub
from pagu.models import Pagudausg

# Create your models here.
VERIF = [
        (0, 'Input Dinas'),
        (1, 'Disetujui'),
    ]

class Rencana(models.Model):
    
    rencana_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    rencana_dana = models.ForeignKey(Subkegiatan, verbose_name='Sumber Dana',on_delete=models.CASCADE)
    rencana_subopd = models.ForeignKey(Subopd, verbose_name='Sub Opd',on_delete=models.CASCADE)
    rencana_kegiatan = models.ForeignKey(DausgpendidikanSub, verbose_name='Sub Kegiatan DAU SG', on_delete=models.CASCADE)
    rencana_pagu = models.DecimalField(verbose_name='Pagu Kegiatan DAU SG',max_digits=17, decimal_places=2,default=0)
    rencana_output = models.DecimalField(verbose_name='Output',max_digits=8, decimal_places=2,default=0)
    rencana_ket = models.TextField(verbose_name='Kode Sub Kegiatan DPA *) cth :  1.01.01.2.01.0001 ', max_length=17)
    rencana_pagudpa = models.DecimalField(verbose_name='Nilai Pagu Sub Kegiatan sesuai DPA',max_digits=17, decimal_places=2,default=0)
    rencana_verif = models.IntegerField(choices=VERIF, default = 0, editable=False)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['rencana_tahun', 'rencana_subopd', 'rencana_kegiatan'], name='unique_rencana')
        ]
    
    def clean(self):
        if Rencana.objects.filter(
            rencana_tahun=self.rencana_tahun,
            rencana_subopd=self.rencana_subopd_id,
            rencana_kegiatan=self.rencana_kegiatan_id
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Rencana Kegiatan untuk Tahun, Sub Opd dan Sub Kegiatan ini sudah ada, silahkan masukkan yang lain.')
        
        total_rencana = self.get_total_rencana(self.rencana_tahun, self.rencana_subopd, self.rencana_dana)
        total_pagudausg = self.get_pagu(self.rencana_tahun, self.rencana_subopd, self.rencana_dana)
    #     total_realisasi_pk = self.get_realisasi_pk()
        
        if self.pk:
            total_rencana = total_rencana - Rencana.objects.get(pk=self.pk).rencana_pagu

        total_rencana += self.rencana_pagu
        
        formatted_total_rencana = "{:,.2f}".format(total_rencana)
        formatted_total_pagudausg = "{:,.2f}".format(total_pagudausg)
        
    #     if self.rencdankel_pagu < total_realisasi_pk :
    #         raise ValidationError(f'Kegiatan ini sudah ada realisasi sebesar Rp. {formatted_total_realisasi_pk} Nilai Rencana tidak boleh lebih kecil dari Nilai Realisasi')
        
        if total_rencana > total_pagudausg:
            raise ValidationError(f'Total rencana anggaran Rp. {formatted_total_rencana} tidak boleh lebih besar dari total Pagu anggaran yang tersedia Rp. {formatted_total_pagudausg}.')
            
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def get_pagu(self,tahun, opd, dana):
        filters = Q(pagudausg_tahun=tahun) & Q(pagudausg_dana=dana)
        if opd is not None and opd not in [124,70]:
            filters &= Q(pagudausg_opd=opd)
        return Pagudausg.objects.filter(filters).aggregate(total_nilai=Sum('pagudausg_nilai'))['total_nilai'] or Decimal(0)
    
    def get_total_rencana(self, tahun, opd, dana):
        filters = Q(rencana_tahun=tahun) & Q(rencana_dana=dana)
        if opd is not None and opd not in [124,70]:
            filters &= Q(rencana_subopd=opd)
        return Rencana.objects.filter(filters).aggregate(total_nilai=Sum('rencana_pagu'))['total_nilai'] or Decimal(0)
    
       
    def get_sisa(self, tahun, opd, dana):
        total_rencana = self.get_total_rencana(tahun, opd, dana)
        total_pagu = self.get_pagu(tahun, opd, dana)
        return total_pagu - total_rencana
    
    # def get_realisasi_pk(self):
    #     filters = Q(realisasidankel_tahun=self.rencdankel_tahun) & Q(realisasidankel_dana=self.rencdankel_dana_id) & Q(realisasidankel_idrencana_id = self.id)
    #     if self.rencdankel_subopd is not None:
    #         filters &= Q(realisasidankel_subopd=self.rencdankel_subopd_id)
    #     nilai_realisasi = RealisasiDankel.objects.filter(filters).aggregate(total_nilai=Sum('realisasidankel_lpjnilai'))['total_nilai'] or Decimal(0)
    #     print(f"nilai realisasi : {nilai_realisasi} dan {filters}")
    #     return nilai_realisasi

    def __str__(self):
        return f"{self.rencana_kegiatan}"

class Rencanaposting(models.Model):
    VERIF = [
        (1, 'Rencana Induk'),
        (2, 'Rencana Perubahan'),
    ]
    posting_rencanaid = models.ForeignKey(Rencana, verbose_name='Id Rencana', on_delete=models.CASCADE)
    posting_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    posting_dana = models.ForeignKey(Subkegiatan, verbose_name='Sumber Dana',on_delete=models.CASCADE)
    posting_subopd = models.ForeignKey(Subopd, verbose_name='Sub Opd',on_delete=models.CASCADE)
    posting_subkegiatan = models.ForeignKey(DausgpendidikanSub, verbose_name='Sub Kegiatan DAU SG', on_delete=models.CASCADE)
    posting_pagu = models.DecimalField(verbose_name='Pagu Kegiatan DAU SG',max_digits=17, decimal_places=2,default=0)
    posting_output = models.DecimalField(verbose_name='Output',max_digits=8, decimal_places=2,default=0)
    posting_ket = models.TextField(verbose_name='Kode Sub Kegiatan DPA *) cth :  1.01.01.2.01.0001 ', max_length=17)
    posting_pagudpa = models.DecimalField(verbose_name='Nilai Pagu Sub Kegiatan sesuai DPA',max_digits=17, decimal_places=2,default=0)
    posting_jadwal = models.IntegerField(verbose_name='Posting Jadwal', choices=VERIF, null=True)
    
    def get_total_rencana(self, tahun, opd, dana):
        filters = Q(posting_tahun=tahun) & Q(posting_dana=dana)
        if opd is not None and opd not in [124,70]:
            filters &= Q(posting_subopd=opd)
        return Rencanaposting.objects.filter(filters).aggregate(total_nilai=Sum('posting_pagu'))['total_nilai'] or Decimal(0)
    
    def __str__(self):
        return f"{self.posting_subkegiatan}"
    

class Realisasi(models.Model):
    realisasi_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    realisasi_dana = models.ForeignKey(Subkegiatan, verbose_name='Sumber Dana',on_delete=models.CASCADE)
    realisasi_tahap = models.ForeignKey(TahapDana, verbose_name='Tahap Realisasi',on_delete=models.CASCADE)
    realisasi_subopd = models.ForeignKey(Subopd, verbose_name='Sub Opd',on_delete=models.CASCADE)
    realisasi_rencanaposting = models.ForeignKey(Rencanaposting, verbose_name='Kegiatan', on_delete=models.CASCADE)
    realisasi_rencana = models.ForeignKey(Rencana, verbose_name="Id Rencana", on_delete=models.CASCADE, editable=False)
    realisasi_kegiatan = models.ForeignKey(DausgpendidikanSub, verbose_name='Sub Kegiatan DAU SG', on_delete=models.CASCADE, editable=False)
    realisasi_output = models.IntegerField(verbose_name='Capaian Output')
    realisasi_sp2d = models.CharField(verbose_name='No SP2D', max_length=100, unique=True)
    realisasi_tgl = models.DateField(verbose_name='Tanggal SP2D')
    realisasi_nilai = models.DecimalField(verbose_name='Nilai SP2D', max_digits=17, decimal_places=2,default=0)
    realisasi_verif = models.IntegerField(choices=VERIF, default = 0, editable=False) 
    
    def clean(self):
        super().clean()
        
#         total_penerimaan = self.get_penerimaan_total(self.realisasidankel_tahun, self.realisasidankel_subopd_id, self.realisasidankel_dana_id)
#         total_realisasi = self.get_realisasilpj_total(self.realisasidankel_tahun, self.realisasidankel_subopd_id, self.realisasidankel_dana_id)
#         total_rencana_pk = self.get_rencana_pk()
#         total_realisasi_pk = self.get_realisasi_pk()
#         total_rencanaoutput_pk = self.get_rencanaoutput_pk()
        
         
        
#         if self.pk:
#             total_realisasi_pk = total_realisasi_pk - RealisasiDankel.objects.get(pk=self.pk).realisasidankel_lpjnilai
#             total_realisasi = total_realisasi - RealisasiDankel.objects.get(pk=self.pk).realisasidankel_lpjnilai
        
#         total_realisasi_pk += self.realisasidankel_lpjnilai
#         total_realisasi += self.realisasidankel_lpjnilai
        
#         # Format nilai menjadi string dengan pemisah ribuan
#         formatted_total_rencana_pk = "{:,.2f}".format(total_rencana_pk)
#         formatted_total_realisasi_pk = "{:,.2f}".format(total_realisasi_pk)
#         formatted_total_realisasi = "{:,.2f}".format(total_realisasi)
#         formatted_total_penerimaan = "{:,.2f}".format(total_penerimaan)
        
#         try:
#             sp2dtu = Decimal(self.realisasidankel_nilai)
#             lpj = Decimal(self.realisasidankel_lpjnilai)
#             sts = Decimal(self.realisasidankel_stsnilai)
#             output = Decimal(self.realisasidankel_output or 0)
            
#         except ValueError:
#             raise ValidationError('SP2D TU dan LPJ harus berupa angka.')
        
#         if output > total_rencanaoutput_pk:
#             raise ValidationError(f'Output tidak boleh lebih besar dari {total_rencanaoutput_pk}')
       
#         if sp2dtu < 0:
#             raise ValidationError('SP2D TU tidak boleh kurang dari 0')
    
#         if lpj > sp2dtu:
#             raise ValidationError('Nilai LPJ tidak boleh lebih besar dari SP2D TU')

#         sisasts = sp2dtu - lpj

#         if sts < 0:
#             raise ValidationError('Nilai STS tidak boleh lebih kecil dari 0')

#         if sts != sisasts:
#             raise ValidationError(f'Nilai STS harus sama dengan {sisasts}')        

        
#         if total_realisasi_pk > total_rencana_pk:
#             raise ValidationError(f'Total Realisasi Kegiatan ini setelah ditambah nilai LPJ sekarang sebesar Rp. {formatted_total_realisasi_pk} tidak boleh lebih besar dari Rp. {formatted_total_rencana_pk} Nilai Rencana Kegiatan yang tersedia.')
        
#         if total_realisasi > total_penerimaan:
#             raise ValidationError(f'Total Realisasi Kegiatan Rp. {formatted_total_realisasi} tidak boleh lebih besar dari Rp. {formatted_total_penerimaan} Total Penerimaan yang tersedia.')
        
    def save(self, *args, **kwargs):
        self.full_clean()
        if self.realisasi_rencanaposting:
            self.realisasi_rencana = self.realisasi_rencanaposting.rencana_id
            self.realisasi_kegiatan = self.realisasi_kegiatan.dausgpendidikansub_id
        super().save(*args, **kwargs)

#     def get_penerimaan_total(self, tahun, opd, dana):
#         filters = Q(distri_penerimaan__penerimaan_tahun=tahun) & Q(distri_penerimaan__penerimaan_dana=dana)
#         if opd is not None and opd != 124 and opd != 70:
#             filters &= Q(distri_subopd=opd)
#         # print(filters)
#         return DistribusiPenerimaan.objects.filter(filters).aggregate(total_nilai=Sum('distri_nilai'))['total_nilai'] or Decimal(0)

#     def get_realisasilpj_total(self, tahun, opd, dana):
#         filters = Q(realisasidankel_tahun=tahun) & Q(realisasidankel_dana=dana)
#         if opd is not None and opd != 124 and opd != 70:
#             filters &= Q(realisasidankel_subopd=opd)
#         return RealisasiDankel.objects.filter(filters).aggregate(total_nilai=Sum('realisasidankel_lpjnilai'))['total_nilai'] or Decimal(0)

#     def get_persentase(self, tahun, opd, dana):
#         try:
#             lpj = self.get_realisasilpj_total(tahun, opd, dana)
#             penerimaan = self.get_penerimaan_total(tahun, opd, dana)
            
#             if lpj is None:
#                 return None
#             if penerimaan is None:
#                 return 0
#             return ((lpj / penerimaan) * 100)
        
#         except ZeroDivisionError:
#             return "Error: Pembagian tidak terdefinisi"  # Menangani pembagian dengan nol
#         except Exception as e:
#             return 0

#     def get_rencana_pk(self):
#         filters = Q(rencdankel_tahun=self.realisasidankel_tahun) & Q(rencdankel_dana_id=self.realisasidankel_dana_id)
#         if self.realisasidankel_subopd_id is not None:
#             filters &= Q(rencdankel_subopd_id=self.realisasidankel_subopd_id)
#         if self.realisasidankel_rencana_id is not None:
#             filters &= Q(id=self.realisasidankel_rencana_id)
        
#         nilai_rencana = RencDankeljadwal.objects.filter(filters).aggregate(total_nilai=Sum('rencdankel_pagu'))['total_nilai'] or Decimal(0)
#         # print(f"nilai rencana : {nilai_rencana} dan {filters}")
#         return nilai_rencana
    
#     def get_rencanaoutput_pk(self):
#         filters = Q(rencdankel_tahun=self.realisasidankel_tahun) & Q(rencdankel_dana_id=self.realisasidankel_dana_id)
#         if self.realisasidankel_subopd_id is not None:
#             filters &= Q(rencdankel_subopd_id=self.realisasidankel_subopd_id)
#         if self.realisasidankel_rencana_id is not None:
#             filters &= Q(id=self.realisasidankel_rencana_id)
        
#         nilai_output = RencDankeljadwal.objects.filter(filters).aggregate(total_nilai=Sum('rencdankel_output'))['total_nilai'] or Decimal(0)
#         # print(f"nilai rencana : {nilai_rencana} dan {filters}")
#         return nilai_output

#     def get_realisasi_pk(self):
#         filters = Q(realisasidankel_tahun=self.realisasidankel_tahun) & Q(realisasidankel_dana=self.realisasidankel_dana_id)
#         if self.realisasidankel_rencana_id:
#             realisasidankel_idrencana = self.realisasidankel_rencana.rencdankel_id
#             filters &= Q(realisasidankel_idrencana = realisasidankel_idrencana)
            
#         if self.realisasidankel_subopd_id is not None:
#             filters &= Q(realisasidankel_subopd=self.realisasidankel_subopd_id)
        
#         nilai_realisasi = RealisasiDankel.objects.filter(filters).aggregate(total_nilai=Sum('realisasidankel_lpjnilai'))['total_nilai'] or Decimal(0)
#         # print(f"nilai realisasi : {nilai_realisasi} dan {filters}")
#         return nilai_realisasi
        
    def __str__(self):
        return f'{self.realisasi_rencanaposting}'