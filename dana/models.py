from django.db import models

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

    def __str__(self):
        return self.subrinc_nama
    
class TahapDana(models.Model):
    tahap_dana = models.CharField(verbose_name="Dana", max_length=50)

    def __str__(self):
        return self.tahap_dana

