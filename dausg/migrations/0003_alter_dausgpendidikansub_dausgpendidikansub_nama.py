# Generated by Django 4.2.11 on 2024-08-23 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dausg', '0002_remove_dankelprog_dankel_subrinc_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dausgpendidikansub',
            name='dausgpendidikansub_nama',
            field=models.CharField(max_length=500, verbose_name='Sub Kegiatan DAUSG Pendidikan'),
        ),
    ]
