from django.db import models
from django.core import validators

class Opd(models.Model):
    kode_opd = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            validators.RegexValidator(
                regex='^[0-9]+$',
                message='Kode OPD harus berupa angka')
            
            ]
        
        )
    nama_opd = models.CharField(
        max_length=100,
        validators=[
            validators.MinLengthValidator(
                limit_value=3,
                message='Gak boleh lebih dari 3')
            ]
        )
    
    def __str__(self):
        return self.nama_opd

    