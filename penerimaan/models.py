from django.db import models
from dana.models import Subrinc, TahapDana
# Create your models here.

class Penerimaan(models.Model):
    penerimaan_dana = models.ForeignKey(Subrinc, verbose_name="Dana", on_delete=models.CASCADE)
    penerimaan_tahap = models.ForeignKey(TahapDana, verbose_name="Tahap", on_delete=models.CASCADE)
    penerimaan_tgl = models.DateField(verbose_name="Tanggal")
    penerimaan_ket = models.CharField(verbose_name="Keterangan", max_length=200)
    penerimaan_nilai = models.DecimalField(verbose_name="Nilai Uang", default=0, max_digits=17 ,decimal_places=2)
    
    def __str__(self):
        return self.penerimaan_ket
    
    
    
    
    