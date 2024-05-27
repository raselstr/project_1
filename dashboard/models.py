from django.db import models
from django.contrib.auth.models import User

class Menu(models.Model):
    menu_nama = models.CharField(max_length=25)
    menu_icon = models.CharField(max_length=30)
    menu_link = models.CharField(max_length=25)

    def __str__(self):
        return self.menu_nama

class Submenu(models.Model):
    submenu_menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    submenu_nama = models.CharField(max_length=20)
    submenu_icon = models.CharField(max_length=30)
    submenu_link = models.CharField(max_length=25)

    def __str__(self):
        return f'{self.submenu_nama} - {self.submenu_menu}'

class Level(models.Model):
    level_nama = models.CharField(max_length=20)
    level_submenu = models.ManyToManyField(Submenu)
    level_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.level_nama
