from django.db import models
from project.validations import *

class Opd(models.Model):
    kode_opd = models.CharField(
        verbose_name="Kode OPD",
        max_length=10,
        unique=True,
        error_messages={'unique': 'Data, nilai ini sudah ada dalam database.'},
        validators=[
            number_validator,
            # partial(unik, app_name='opd', model_name='Opd', field='kode_opd')
            ]
        )
    
    nama_opd = models.CharField(
        verbose_name="Nama OPD",
        max_length=100,
        unique=True,
        error_messages={'unique': 'Maaf, nilai ini sudah ada dalam database.'},
        validators=[
            minimal2_validator,
            
            ]
        )

    def __str__(self):
        return self.nama_opd

class Author(models.Model):
    name = models.CharField(max_length=100)
    birthdate = models.DateField(null=True, blank=True)
    biography = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Publisher(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100)
    publication_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
