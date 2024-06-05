from django.db import models
from dana.models import Subrinc, Dana

# Create your models here.
class DankelProg (models.Model):
    dankel_dana = models.ForeignKey(Dana, on_delete=models.CASCADE)
    dankel_subrinc = models.ForeignKey(Subrinc, on_delete=models.CASCADE)
    dankel_prog = models.CharField(max_length=200)
    
    def __str__(self):
        return self.dankel_prog

class DankelKeg (models.Model):
    dankelkeg_subrinc = models.ForeignKey(Subrinc, on_delete=models.CASCADE)
    dankelkeg_prog = models.ForeignKey(DankelProg, on_delete=models.CASCADE)
    dankelkeg_nama = models.CharField(max_length=200)
    
    def __str__(self):
        return self.dankelkeg_nama