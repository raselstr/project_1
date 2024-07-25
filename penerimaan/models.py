from django.db import models, IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import datetime
from django.db.models import UniqueConstraint
from dana.models import Kegiatan, TahapDana
from opd.models import Subopd
# Create your models here.

class Penerimaan(models.Model):
    penerimaan_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    penerimaan_dana = models.ForeignKey(Kegiatan, verbose_name="Dana", on_delete=models.CASCADE)
    penerimaan_tahap = models.ForeignKey(TahapDana, verbose_name="Tahap", on_delete=models.CASCADE)
    penerimaan_tgl = models.DateField(verbose_name="Tanggal")
    penerimaan_ket = models.CharField(verbose_name="Keterangan", max_length=200)
    penerimaan_nilai = models.DecimalField(verbose_name="Nilai Uang", default=0, max_digits=17 ,decimal_places=2)
    
    def __str__(self):
        return self.penerimaan_ket
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['penerimaan_tahun', 'penerimaan_dana', 'penerimaan_tahap'], name='unique_penerimaan')
        ]
    
class DistribusiPenerimaan(models.Model):
    distri_penerimaan = models.ForeignKey(Penerimaan, verbose_name='Penerimaan', on_delete=models.CASCADE)
    distri_subopd = models.ForeignKey(Subopd, verbose_name='OPD Penerima', on_delete=models.CASCADE)
    distri_nilai = models.DecimalField(verbose_name='Nilai Distribusi', max_digits=17, decimal_places=2,default=0)   
    distri_ket = models.CharField(verbose_name='Keterangan Distribusi', max_length=50)   
    
    def __str__(self):
        return f'{self.distri_penerimaan.penerimaan_dana} {self.distri_penerimaan.penerimaan_tahap} - {self.distri_subopd}'
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['distri_penerimaan', 'distri_subopd'], name='unique_distrib')
        ]
    
    def clean(self):
        # Validasi unique constraint
        if DistribusiPenerimaan.objects.filter(
            distri_penerimaan=self.distri_penerimaan,
            distri_subopd=self.distri_subopd
        ).exclude(pk=self.pk).exists():
            raise ValidationError("Kombinasi Penerimaan Dana dan OPD sudah digunakan.")
       
       # Hitung total distribusi untuk penerimaan ini
        total_distribusi = DistribusiPenerimaan.objects.filter(distri_penerimaan=self.distri_penerimaan).aggregate(total=Sum('distri_nilai'))['total'] or Decimal(0)
        
        if self.pk:
            # Jika instance sudah ada, kurangi nilai lama dari total
            total_distribusi -= DistribusiPenerimaan.objects.get(pk=self.pk).distri_nilai
        
        total_distribusi += self.distri_nilai
        
        # Validasi total distribusi tidak boleh melebihi penerimaan_nilai
        if total_distribusi > self.distri_penerimaan.penerimaan_nilai:
            raise ValidationError(f'Total distribusi {total_distribusi} melebihi nilai penerimaan {self.distri_penerimaan.penerimaan_nilai}')
    
    def save(self, *args, **kwargs):
        self.clean()  # Panggil clean untuk menjalankan validasi sebelum save
        super(DistribusiPenerimaan, self).save(*args, **kwargs)
        