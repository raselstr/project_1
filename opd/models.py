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
