from django.db import models
from dana.models import Subkegiatan

# Create your models here.
class DankelProg (models.Model):
    dankel_dana = models.ForeignKey(Subkegiatan, verbose_name="Dana", on_delete=models.CASCADE)
    dankel_prog = models.CharField(verbose_name="Program Dana Kelurahan", max_length=200)
    
    def __str__(self):
        return self.dankel_prog

class DankelKeg (models.Model):
    dankelkeg_prog = models.ForeignKey(DankelProg, verbose_name="Program Dana Kelurahan", on_delete=models.CASCADE, related_name='dankelkegs')
    dankelkeg_nama = models.CharField(verbose_name="Kegiatan Dana Kelurahan", max_length=200)
    
    def __str__(self):
        return self.dankelkeg_nama

class Dankelsub (models.Model):
    dankelsub_keg = models.ForeignKey(DankelKeg, verbose_name="Kegiatan Dana Kelurahan", on_delete=models.CASCADE, related_name='dankelsubs')
    dankelsub_nama = models.CharField(verbose_name="Sub Kegiatan Dana Kelurahan",max_length=200)
    dankelsub_satuan = models.CharField(verbose_name="Satuan",max_length=200)
    
    def __str__(self):
        return f'{self.dankelsub_keg} - {self.dankelsub_nama}'


class DausgpendidikanProg (models.Model):
    dausgpendidikan_dana = models.ForeignKey(Subkegiatan, verbose_name="Dana", on_delete=models.CASCADE)
    dausgpendidikan_prog = models.CharField(verbose_name="Program DAUSG Pendidikan", max_length=200)
    
    def __str__(self):
        return self.dausgpendidikan_prog

class DausgpendidikanKeg (models.Model):
    dausgpendidikankeg_prog = models.ForeignKey(DausgpendidikanProg, verbose_name="Program DAUSG Pendidikan", on_delete=models.CASCADE, related_name='dausgpendidikankegs')
    dausgpendidikankeg_nama = models.CharField(verbose_name="Kegiatan DAUSG Pendidikan", max_length=200)
    
    def __str__(self):
        return self.dausgpendidikankeg_nama

class DausgpendidikanSub (models.Model):
    dausgpendidikansub_keg = models.ForeignKey(DausgpendidikanKeg, verbose_name="Kegiatan DAUSG Pendidikan", on_delete=models.CASCADE, related_name='dausgpendidikansubs')
    dausgpendidikansub_nama = models.CharField(verbose_name="Sub Kegiatan DAUSG Pendidikan",max_length=200)
    dausgpendidikansub_satuan = models.CharField(verbose_name="Satuan",max_length=200)
    
    def __str__(self):
        return f'{self.dausgpendidikansub_keg} - {self.dausgpendidikansub_nama}'

class DausgkesehatanProg (models.Model):
    dausgkesehatan_dana = models.ForeignKey(Subkegiatan, verbose_name="Dana", on_delete=models.CASCADE)
    dausgkesehatan_prog = models.CharField(verbose_name="Program DAUSG kesehatan", max_length=200)
    
    def __str__(self):
        return self.dausgkesehatan_prog

class DausgkesehatanKeg (models.Model):
    dausgkesehatankeg_prog = models.ForeignKey(DausgkesehatanProg, verbose_name="Program DAUSG kesehatan", on_delete=models.CASCADE, related_name='dausgkesehatankegs')
    dausgkesehatankeg_nama = models.CharField(verbose_name="Kegiatan DAUSG kesehatan", max_length=200)
    
    def __str__(self):
        return self.dausgkesehatankeg_nama

class DausgkesehatanSub (models.Model):
    dausgkesehatansub_keg = models.ForeignKey(DausgkesehatanKeg, verbose_name="Kegiatan DAUSG kesehatan", on_delete=models.CASCADE, related_name='dausgkesehatansubs')
    dausgkesehatansub_nama = models.CharField(verbose_name="Sub Kegiatan DAUSG kesehatan",max_length=200)
    dausgkesehatansub_satuan = models.CharField(verbose_name="Satuan",max_length=200)
    
    def __str__(self):
        return f'{self.dausgkesehatansub_keg} - {self.dausgkesehatansub_nama}'


class DausgpuProg (models.Model):
    dausgpu_dana = models.ForeignKey(Subkegiatan, verbose_name="Dana", on_delete=models.CASCADE)
    dausgpu_prog = models.CharField(verbose_name="Program DAUSG Pekerjaan Umum", max_length=200)
    
    def __str__(self):
        return self.dausgpu_prog

class DausgpuKeg (models.Model):
    dausgpukeg_prog = models.ForeignKey(DausgpuProg, verbose_name="Program DAUSG Pekerjaan Umum", on_delete=models.CASCADE, related_name='dausgpukegs')
    dausgpukeg_nama = models.CharField(verbose_name="Kegiatan DAUSG Pekerjaan Umum", max_length=200)
    
    def __str__(self):
        return self.dausgpukeg_nama

class DausgpuSub (models.Model):
    dausgpusub_keg = models.ForeignKey(DausgpuKeg, verbose_name="Kegiatan DAUSG Pekerjaan Umum", on_delete=models.CASCADE, related_name='dausgpusubs')
    dausgpusub_nama = models.CharField(verbose_name="Sub Kegiatan DAUSG Pekerjaan Umum",max_length=200)
    dausgpusub_satuan = models.CharField(verbose_name="Satuan",max_length=200)
    
    def __str__(self):
        return f'{self.dausgpusub_keg} - {self.dausgpusub_nama}'