from django.db import models
from django.db.models.signals import pre_delete
from django.core.exceptions import ValidationError
from django.utils.text import slugify

class Dana(models.Model):
    dana_nama = models.CharField(verbose_name="Dana", max_length=30)

    def __str__(self):
        return f'{self.id}.{self.dana_nama}'
    
class Program(models.Model):
    program_dana = models.ForeignKey(Dana, verbose_name="Dana", on_delete=models.CASCADE)
    program_nama = models.CharField(verbose_name="Program", max_length=200)

    def __str__(self):
        return self.program_nama
    
class Kegiatan(models.Model):
    kegiatan_dana = models.ForeignKey(Dana, verbose_name="Dana", on_delete=models.CASCADE)
    kegiatan_program = models.ForeignKey(Program, verbose_name="Program", on_delete=models.CASCADE)
    kegiatan_nama = models.CharField(verbose_name="Kegiatan", max_length=200)

    def __str__(self):
        return self.kegiatan_nama
    
class Subkegiatan(models.Model):
    sub_dana = models.ForeignKey(Dana, verbose_name="Dana", on_delete=models.CASCADE)
    sub_prog = models.ForeignKey(Program, verbose_name="Program", on_delete=models.CASCADE)
    sub_keg  = models.ForeignKey(Kegiatan, verbose_name="Kegiatan", on_delete=models.CASCADE)
    sub_nama = models.CharField(verbose_name="Sub Kegiatan", max_length=200)

    def __str__(self):
        return self.sub_nama
    
class Subrinc(models.Model):
    subrinc_dana = models.ForeignKey(Dana, verbose_name="Dana", on_delete=models.CASCADE)
    subrinc_prog = models.ForeignKey(Program, verbose_name="Program", on_delete=models.CASCADE)
    subrinc_keg  = models.ForeignKey(Kegiatan, verbose_name="Kegiatan", on_delete=models.CASCADE)
    subrinc_kegsub  = models.ForeignKey(Subkegiatan, verbose_name="Sub Kegiatan", on_delete=models.CASCADE)
    subrinc_nama = models.CharField(verbose_name="Rincian Sub Kegiatan", max_length=200)
    subrinc_slug = models.SlugField(unique=True, allow_unicode=True, editable=False)
    
    def save(self, *args, **kwargs):
        if not self.subrinc_slug or self.subrinc_nama != self._meta.get_field('subrinc_nama').value_from_object(self):
            self.subrinc_slug = slugify(self.subrinc_nama)
        super().save(*args, **kwargs)
            
    def __str__(self):
        return self.subrinc_nama
    
class TahapDana(models.Model):
    tahap_dana = models.CharField(verbose_name="Dana", max_length=50)

    def __str__(self):
        return self.tahap_dana

# Sinyal untuk mencegah penghapusan objek Dana jika terkait dengan objek lain
def prevent_dana_deletion(sender, instance, **kwargs):
    if Program.objects.filter(program_dana=instance).exists() or \
       Kegiatan.objects.filter(kegiatan_dana=instance).exists() or \
       Subkegiatan.objects.filter(sub_dana=instance).exists() or \
       Subrinc.objects.filter(subrinc_dana=instance).exists():
        raise ValidationError("Dana tidak bisa dihapus karena terhubung dengan data lain.")

# Sinyal untuk mencegah penghapusan objek Program jika terkait dengan objek lain
def prevent_program_deletion(sender, instance, **kwargs):
    if Kegiatan.objects.filter(kegiatan_program=instance).exists() or \
       Subkegiatan.objects.filter(sub_prog=instance).exists() or \
       Subrinc.objects.filter(subrinc_prog=instance).exists():
        raise ValidationError("Program tidak bisa dihapus karena terhubung dengan data lain.")

# Sinyal untuk mencegah penghapusan objek Kegiatan jika terkait dengan objek lain
def prevent_kegiatan_deletion(sender, instance, **kwargs):
    if Subkegiatan.objects.filter(sub_keg=instance).exists() or \
       Subrinc.objects.filter(subrinc_keg=instance).exists():
        raise ValidationError("Kegiatan tidak bisa dihapus karena terhubung dengan data lain..")

# Sinyal untuk mencegah penghapusan objek Subkegiatan jika terkait dengan objek lain
def prevent_subkegiatan_deletion(sender, instance, **kwargs):
    if Subrinc.objects.filter(subrinc_kegsub=instance).exists():
        raise ValidationError("Subkegiatan tidak bisa dihapus karena terhubung dengan data lain.")

# Menghubungkan sinyal dengan model masing-masing
pre_delete.connect(prevent_dana_deletion, sender=Dana)
pre_delete.connect(prevent_program_deletion, sender=Program)
pre_delete.connect(prevent_kegiatan_deletion, sender=Kegiatan)
pre_delete.connect(prevent_subkegiatan_deletion, sender=Subkegiatan)