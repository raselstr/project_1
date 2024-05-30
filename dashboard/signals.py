from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Userlevel, Level

@receiver(post_save, sender=User)
def create_userlevel(sender, instance, created, **kwargs):
    if created:
        # Tentukan level default yang ingin Anda gunakan, misalnya:
        default_level = Level.objects.get(level_nama='Pengguna')  # ganti dengan logika Anda
        Userlevel.objects.create(user_nama=instance, userlevel=default_level)