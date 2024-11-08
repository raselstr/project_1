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
from penerimaan.models import Penerimaan

model_opd = Subopd
model_dana = Subkegiatan
model_tahap = TahapDana
model_subkegiatan = DausgpendidikanSub
model_pagu = Pagudausg
model_penerimaan = Penerimaan

# Create your models here.
VERIF = [
        (0, 'Input Dinas'),
        (1, 'Disetujui'),
    ]

class BaseRencana(models.Model):
    rencana_tahun = models.IntegerField(verbose_name="Tahun", default=datetime.now().year)
    rencana_dana = models.ForeignKey('dana.Subkegiatan', verbose_name='Sumber Dana', on_delete=models.CASCADE)
    rencana_subopd = models.ForeignKey('opd.Subopd', verbose_name='Sub Opd', on_delete=models.CASCADE)
    rencana_kegiatan = models.ForeignKey('dausg.DausgpendidikanSub', verbose_name='Sub Kegiatan DAU SG', on_delete=models.CASCADE)
    rencana_pagu = models.DecimalField(verbose_name='Pagu Kegiatan DAU SG', max_digits=17, decimal_places=2, default=0)
    rencana_output = models.DecimalField(verbose_name='Output', max_digits=8, decimal_places=2, default=0)
    rencana_ket = models.TextField(verbose_name='Kode Sub Kegiatan DPA *) contoh: 1.01.01.2.01.0001', max_length=17)
    rencana_pagudpa = models.DecimalField(verbose_name='Nilai Pagu Sub Kegiatan sesuai DPA', max_digits=17, decimal_places=2, default=0)
    rencana_verif = models.IntegerField(choices=VERIF, default=0, editable=False)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        # Cek apakah model ini adalah Rencana atau Rencanasisa
        model_class = self.__class__

        # Lakukan pengecekan unik hanya pada model yang sedang digunakan
        if model_class.objects.filter(
            rencana_tahun=self.rencana_tahun,
            rencana_subopd=self.rencana_subopd_id,
            rencana_kegiatan=self.rencana_kegiatan_id
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Rencana Kegiatan untuk Tahun, Sub Opd, dan Sub Kegiatan ini sudah ada. Silakan masukkan data yang lain.')
        
        # Lanjutkan dengan logika validasi lainnya
        total_rencana = self.get_total_rencana(self.rencana_tahun, self.rencana_subopd, self.rencana_dana_id)
        total_pagudausg = self.get_pagu(self.rencana_tahun, self.rencana_subopd, self.rencana_dana_id)

        if self.pk:
            total_rencana -= self.__class__.objects.get(pk=self.pk).rencana_pagu

        total_rencana += self.rencana_pagu

        if total_rencana > total_pagudausg:
            raise ValidationError(
                f'Total rencana anggaran Rp. {total_rencana:,.2f} tidak boleh lebih besar dari total Pagu anggaran yang tersedia Rp. {total_pagudausg:,.2f}.'
            )

    def save(self, *args, **kwargs):
        total_realisasi_pk = 0
        if self.pk:
            original = self.__class__.objects.get(pk=self.pk)
            if original.rencana_kegiatan_id != self.rencana_kegiatan_id:
                total_realisasi_pk = self.get_realisasi_pk(original.rencana_kegiatan_id)
                if total_realisasi_pk > 0:
                    raise ValidationError('Tidak bisa mengubah "Sub Kegiatan DAU SG" karena sudah ada realisasi.')

        if self.rencana_pagu < total_realisasi_pk:
            raise ValidationError(
                f'Kegiatan ini sudah ada realisasi sebesar Rp. {total_realisasi_pk:,.2f}. Nilai Rencana Rp. {self.rencana_pagu:,.2f} tidak boleh lebih kecil dari Nilai Realisasi'
            )

        super().save(*args, **kwargs)

    def get_pagu(self, tahun, opd, dana):
        filters = Q(pagudausg_tahun=tahun) & Q(pagudausg_dana=dana)
        if opd and opd not in [124, 70]:
            filters &= Q(pagudausg_opd=opd)
        return model_pagu.objects.filter(filters).aggregate(total_nilai=Sum('pagudausg_nilai'))['total_nilai'] or Decimal(0)

    def get_total_rencana(self, tahun, opd, dana):
        filters = Q(rencana_tahun=tahun) & Q(rencana_dana=dana)
        if opd and opd not in [124, 70]:
            filters &= Q(rencana_subopd=opd)
        return self.__class__.objects.filter(filters).aggregate(total_nilai=Sum('rencana_pagu'))['total_nilai'] or Decimal(0)
    
    def get_realisasi_pk(self, kode):
        filters = Q(realisasi_tahun=self.rencana_tahun) & Q(realisasi_dana=self.rencana_dana_id)
        if self.rencana_kegiatan_id:
            filters &= Q(realisasi_subkegiatan_id=kode)
        if self.rencana_subopd_id:
            filters &= Q(realisasi_subopd=self.rencana_subopd_id)
        return Realisasi.objects.filter(filters).aggregate(total_nilai=Sum('realisasi_nilai'))['total_nilai'] or Decimal(0)

    def __str__(self):
        return str(self.rencana_kegiatan)


class Rencana(BaseRencana):
    class Meta(BaseRencana.Meta):
        constraints = [
            UniqueConstraint(fields=['rencana_tahun', 'rencana_subopd', 'rencana_kegiatan'], name='unique_rencana')
        ]
        db_table = 'pendidikan_rencana'


class Rencanasisa(BaseRencana):
    class Meta(BaseRencana.Meta):
        constraints = [
            UniqueConstraint(fields=['rencana_tahun', 'rencana_subopd', 'rencana_kegiatan'], name='unique_rencanasisa')
        ]
        db_table = 'pendidikan_rencanasisa'

class BaseRencanaposting(models.Model):
    VERIF = [
        (1, 'Rencana Induk'),
        (2, 'Rencana Perubahan'),
    ]
    
    posting_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    posting_dana = models.ForeignKey('dana.Subkegiatan', verbose_name='Sumber Dana',on_delete=models.CASCADE)
    posting_subopd = models.ForeignKey('opd.Subopd', verbose_name='Sub Opd',on_delete=models.CASCADE)
    posting_subkegiatan = models.ForeignKey('dausg.DausgpendidikanSub', verbose_name='Sub Kegiatan DAU SG', on_delete=models.CASCADE)
    posting_pagu = models.DecimalField(verbose_name='Pagu Kegiatan DAU SG',max_digits=17, decimal_places=2,default=0)
    posting_output = models.DecimalField(verbose_name='Output',max_digits=8, decimal_places=2,default=0)
    posting_ket = models.TextField(verbose_name='Kode Sub Kegiatan DPA *) contoh :  1.01.01.2.01.0001 ', max_length=17)
    posting_pagudpa = models.DecimalField(verbose_name='Nilai Pagu Sub Kegiatan sesuai DPA',max_digits=17, decimal_places=2,default=0)
    posting_jadwal = models.IntegerField(verbose_name='Posting Jadwal', choices=VERIF, null=True)
    
    class Meta:
        abstract = True
        
    def get_total_rencana(self, tahun, opd, dana):
        filters = Q(posting_tahun=tahun) & Q(posting_dana=dana)
        if opd is not None and opd not in [124,67,70]:
            filters &= Q(posting_subopd=opd)
        return self.__class__.objects.filter(filters).aggregate(total_nilai=Sum('posting_pagu'))['total_nilai'] or Decimal(0)
    
    def __str__(self):
        return f"{self.posting_subkegiatan}"

class Rencanaposting(BaseRencanaposting):
    posting_rencanaid = models.ForeignKey('pendidikan.Rencana', verbose_name='Id Rencana', on_delete=models.CASCADE)
    class Meta(BaseRencanaposting.Meta):
        db_table = 'pendidikan_rencanaposting'

class Rencanapostingsisa(BaseRencanaposting):
    posting_rencanaid = models.ForeignKey('pendidikan.Rencanasisa', verbose_name='Id Rencana', on_delete=models.CASCADE)
    class Meta(BaseRencanaposting.Meta):
        db_table = 'pendidikan_rencanapostingsisa'


class Realisasi(models.Model):
    VERIF = [
        (0, 'Diinput Dinas'),
        (1, 'Disetujui APIP'),
    ]
    realisasi_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    realisasi_dana = models.ForeignKey(Subkegiatan, verbose_name='Sumber Dana',on_delete=models.CASCADE)
    realisasi_tahap = models.ForeignKey(TahapDana, verbose_name='Tahap Realisasi',on_delete=models.CASCADE)
    realisasi_subopd = models.ForeignKey(Subopd, verbose_name='Sub Opd',on_delete=models.CASCADE)
    realisasi_rencanaposting = models.ForeignKey(Rencanaposting, verbose_name='Kegiatan', on_delete=models.CASCADE)
    realisasi_rencana = models.ForeignKey(Rencana, verbose_name="Id Rencana", on_delete=models.CASCADE, editable=False)
    realisasi_subkegiatan = models.ForeignKey(DausgpendidikanSub, verbose_name='Sub Kegiatan DAU SG', on_delete=models.CASCADE, editable=False)
    realisasi_output = models.IntegerField(verbose_name='Capaian Output')
    realisasi_sp2d = models.CharField(verbose_name='No SP2D', max_length=100, unique=True)
    realisasi_tgl = models.DateField(verbose_name='Tanggal SP2D')
    realisasi_nilai = models.DecimalField(verbose_name='Nilai SP2D', max_digits=17, decimal_places=2,default=0)
    realisasi_verif = models.IntegerField(choices=VERIF, default = 0, editable=False, verbose_name='Verifikasi') 
    
    def clean(self):
        super().clean()
        
        total_penerimaan = model_penerimaan().totalpenerimaan(self.realisasi_tahun, self.realisasi_dana)
        total_realisasi = self.get_realisasi_total(self.realisasi_tahun, self.realisasi_subopd_id, self.realisasi_dana_id)
        total_realisasi_pk = self.get_realisasi_pk()
        total_rencana_pk = self.get_rencana_pk()
        total_rencanaoutput_pk = self.get_rencanaoutput_pk()

        if self.pk:
            total_realisasi_pk = total_realisasi_pk - Realisasi.objects.get(pk=self.pk).realisasi_nilai
            total_realisasi = total_realisasi - Realisasi.objects.get(pk=self.pk).realisasi_nilai
        
        total_realisasi_pk += self.realisasi_nilai
        total_realisasi += self.realisasi_nilai
        
# #         # Format nilai menjadi string dengan pemisah ribuan
        formatted_total_rencana_pk = "{:,.2f}".format(total_rencana_pk)
        formatted_total_realisasi_pk = "{:,.2f}".format(total_realisasi_pk)
        formatted_total_realisasi = "{:,.2f}".format(total_realisasi)
        formatted_total_penerimaan = "{:,.2f}".format(total_penerimaan)
        
        
        output = Decimal(self.realisasi_output or 0)
        
        if output < 0:
            raise ValidationError(f'Output tidak boleh lebih kecil dari 0')
        
        if output > total_rencanaoutput_pk:
            raise ValidationError(f'Output tidak boleh lebih besar dari {total_rencanaoutput_pk}')
       
        if total_realisasi_pk > total_rencana_pk:
            raise ValidationError(f'Total Realisasi Kegiatan ini setelah ditambah nilai SP2D sekarang sebesar Rp. {formatted_total_realisasi_pk} tidak boleh lebih besar dari Rp. {formatted_total_rencana_pk} Nilai Rencana Kegiatan yang tersedia.')
        
        if total_realisasi > total_penerimaan:
            raise ValidationError(f'Total Realisasi Kegiatan Rp. {formatted_total_realisasi} tidak boleh lebih besar dari Rp. {formatted_total_penerimaan} Total Penerimaan yang tersedia.')
        
    def save(self, *args, **kwargs):
        self.full_clean()
        if self.realisasi_rencanaposting:
            self.realisasi_rencana_id = self.realisasi_rencanaposting.posting_rencanaid_id
            self.realisasi_subkegiatan_id = self.realisasi_rencanaposting.posting_subkegiatan_id
        # print(f"Nilai realisasi_rencana_id sebelum save: {self.realisasi_rencana_id}")
        # print(f"Nilai realisasi_subkegiatan_id sebelum save: {self.realisasi_subkegiatan_id}")
        super().save(*args, **kwargs)

    def get_realisasi_total(self, tahun, opd, dana):
        filters = Q(realisasi_tahun=tahun) & Q(realisasi_dana=dana)
        if opd is not None and opd not in [124,67,70]:
            filters &= Q(realisasi_subopd=opd)
        return Realisasi.objects.filter(filters).aggregate(total_nilai=Sum('realisasi_nilai'))['total_nilai'] or Decimal(0)

    def get_realisasi_pk(self):
        filters = Q(realisasi_tahun=self.realisasi_tahun) & Q(realisasi_dana=self.realisasi_dana_id)
        if self.realisasi_rencanaposting_id is not None:
            subkegiatan = self.realisasi_rencanaposting.posting_subkegiatan_id
            filters &= Q(realisasi_subkegiatan_id=subkegiatan)
        if self.realisasi_subopd_id is not None:
            filters &= Q(realisasi_subopd=self.realisasi_subopd_id)
        nilai_realisasi = Realisasi.objects.filter(filters).aggregate(total_nilai=Sum('realisasi_nilai'))['total_nilai'] or Decimal(0)
        # print(f"nilai realisasi : {nilai_realisasi}, {self.realisasi_subkegiatan_id} dan {filters}")
        return nilai_realisasi

    def get_rencana_pk(self):
        filters = Q(posting_tahun=self.realisasi_tahun) & Q(posting_dana_id=self.realisasi_dana_id)
        if self.realisasi_rencanaposting_id is not None:
            subkegiatan = self.realisasi_rencanaposting.posting_subkegiatan_id
            filters &= Q(posting_subkegiatan_id=subkegiatan)
        if self.realisasi_subopd_id is not None:
            filters &= Q(posting_subopd_id=self.realisasi_subopd_id)
        
        nilai_rencana = Rencanaposting.objects.filter(filters).aggregate(total_nilai=Sum('posting_pagu'))['total_nilai'] or Decimal(0)
        # print(f"nilai rencana : {nilai_rencana}, {self.realisasi_subkegiatan_id} dan {filters}")
        return nilai_rencana
    
    def get_rencanaoutput_pk(self):
        filters = Q(posting_tahun=self.realisasi_tahun) & Q(posting_dana_id=self.realisasi_dana_id)
        if self.realisasi_subopd_id is not None:
            filters &= Q(posting_subopd_id=self.realisasi_subopd_id)
        if self.realisasi_output is not None:
            filters &= Q(id=self.realisasi_rencanaposting_id)
        
        nilai_output = Rencanaposting.objects.filter(filters).aggregate(total_nilai=Sum('posting_output'))['total_nilai'] or Decimal(0)
        # print(f"nilai rencana : {nilai_rencana} dan {filters}")
        return nilai_output

    def get_persendana(self, tahun, opd, dana):
        try:
            totalrealisasi = self.get_realisasi_total(tahun, opd, dana)
            penerimaan = model_penerimaan().totalpenerimaan(tahun,dana)
            
            if totalrealisasi is None:
                return None
            if penerimaan is None:
                return 0
            return ((totalrealisasi / penerimaan) * 100)
        
        except ZeroDivisionError:
            return "Error: Pembagian tidak terdefinisi"  # Menangani pembagian dengan nol
        except Exception as e:
            return 0
    
    def get_persenpagu(self, tahun, opd, dana):
        try:
            totalrealisasi = self.get_realisasi_total(tahun, opd, dana)
            persenpagu = Rencanaposting().get_total_rencana(tahun, opd, dana)
            
            if totalrealisasi is None:
                return None
            if persenpagu is None:
                return 0
            return ((totalrealisasi / persenpagu) * 100)
        
        except ZeroDivisionError:
            return "Error: Pembagian tidak terdefinisi"  # Menangani pembagian dengan nol
        except Exception as e:
            return 0

    def __str__(self):
        return f'{self.realisasi_rencanaposting}'

