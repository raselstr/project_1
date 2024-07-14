from django.db import models
from django.contrib.auth.models import User
from opd.models import Subopd

class Menu(models.Model):
    menu_nama = models.CharField(
        verbose_name="Menu",
        max_length=30,
        unique=True,
        error_messages={'unique': 'Maaf, data ini sudah ada dalam database.'},
    )
    menu_icon = models.CharField(verbose_name="Icon", max_length=40)
    menu_link = models.CharField(verbose_name="Link", max_length=40, blank=True)

    def __str__(self):
        return self.menu_nama
    
    
class Submenu(models.Model):
    submenu_menu = models.ForeignKey(Menu, verbose_name="Menu", on_delete=models.CASCADE)
    submenu_nama = models.CharField(
        verbose_name="Sub Menu",
        max_length=30,
        )
    submenu_icon = models.CharField(verbose_name="Icon", max_length=40)
    submenu_link = models.CharField(verbose_name="Link", max_length=40, blank=True)

    def __str__(self):
        return f'{self.submenu_menu} - {self.submenu_nama}'

class Level(models.Model):
    level_nama = models.CharField(
        verbose_name="Level",
        max_length=30,
        unique=True,
        error_messages={'unique': 'Maaf, data ini sudah ada dalam database.'},
        )
    
    def __str__(self):
        return self.level_nama

class Levelsub(models.Model):
    levelsub_level = models.ForeignKey(Level, verbose_name='Level', on_delete=models.CASCADE)
    levelsub_submenu = models.ForeignKey(Submenu, verbose_name="Level Sub Menu", on_delete=models.CASCADE)
    lihat = models.BooleanField(default=False, verbose_name="List Data")
    simpan = models.BooleanField(default=False, verbose_name="Simpan Data")
    edit = models.BooleanField(default=False, verbose_name="Update Data")
    hapus = models.BooleanField(default=False, verbose_name="Hapus Data")
    
    def __str__(self):
        return f'{self.levelsub_submenu}'

    
class Userlevel(models.Model):
    user_nama = models.OneToOneField(User, verbose_name="Pengguna", on_delete=models.CASCADE)
    userlevel = models.ForeignKey(Level, verbose_name="Level", on_delete=models.CASCADE)
    userlevelopd = models.ForeignKey(Subopd, verbose_name="Sub OPD", on_delete=models.CASCADE, related_name='userlevel')

    def __str__(self):
        return f'{self.user_nama} - {self.userlevel}'
    
