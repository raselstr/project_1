# Generated by Django 4.2.11 on 2024-09-03 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dausg', '0004_alter_dausgkesehatansub_dausgkesehatansub_nama_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dausgkesehatankeg',
            name='dausgkesehatankeg_nama',
            field=models.CharField(max_length=500, verbose_name='Kegiatan DAUSG kesehatan'),
        ),
        migrations.AlterField(
            model_name='dausgkesehatanprog',
            name='dausgkesehatan_prog',
            field=models.CharField(max_length=500, verbose_name='Program DAUSG kesehatan'),
        ),
        migrations.AlterField(
            model_name='dausgpendidikankeg',
            name='dausgpendidikankeg_nama',
            field=models.CharField(max_length=500, verbose_name='Kegiatan DAUSG Pendidikan'),
        ),
        migrations.AlterField(
            model_name='dausgpendidikanprog',
            name='dausgpendidikan_prog',
            field=models.CharField(max_length=500, verbose_name='Program DAUSG Pendidikan'),
        ),
        migrations.AlterField(
            model_name='dausgpukeg',
            name='dausgpukeg_nama',
            field=models.CharField(max_length=500, verbose_name='Kegiatan DAUSG Pekerjaan Umum'),
        ),
        migrations.AlterField(
            model_name='dausgpuprog',
            name='dausgpu_prog',
            field=models.CharField(max_length=500, verbose_name='Program DAUSG Pekerjaan Umum'),
        ),
    ]
