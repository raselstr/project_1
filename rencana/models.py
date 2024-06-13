from django.db import models
from opd.models import Opd
from datetime import datetime

# Create your models here.
class Rencana(models.Model):
    rencana_tahun = models.IntegerField(verbose_name="Tahun",default=datetime.now().year)
    rencana_opd = models.ForeignKey(Opd, verbose_name='Opd',on_delete=models.CASCADE)
    
    def __str__(self):
        return self.rencana_opd
    