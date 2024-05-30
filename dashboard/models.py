from django.db import models
from django.contrib.auth.models import User
from project.validations import *

class Menu(models.Model):
    menu_nama = models.CharField(
        max_length=30,
        unique=True,
        error_messages={'unique': 'Maaf, data ini sudah ada dalam database.'},
    )
    menu_icon = models.CharField(max_length=40)
    menu_link = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.menu_nama
    
    
class Submenu(models.Model):
    submenu_menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    submenu_nama = models.CharField(
        max_length=30,
        unique=True,
        error_messages={'unique': 'Maaf, data ini sudah ada dalam database.'},
        )
    submenu_icon = models.CharField(max_length=40)
    submenu_link = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return f'{self.submenu_nama} - {self.submenu_menu}'

class Level(models.Model):
    level_nama = models.CharField(
        max_length=30,
        unique=True,
        error_messages={'unique': 'Maaf, data ini sudah ada dalam database.'},
        )
    level_submenu = models.ManyToManyField(Submenu)

    def __str__(self):
        return self.level_nama
    
class Userlevel(models.Model):
    user_nama = models.OneToOneField(User, on_delete=models.CASCADE)
    userlevel = models.ForeignKey(Level, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user_nama} - {self.userlevel}'
    
