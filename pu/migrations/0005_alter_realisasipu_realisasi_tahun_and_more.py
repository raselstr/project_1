# Generated by Django 4.2.11 on 2025-01-21 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pu', '0004_alter_realisasipu_table_alter_rencanapu_table_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realisasipu',
            name='realisasi_tahun',
            field=models.IntegerField(default=2025, verbose_name='Tahun'),
        ),
        migrations.AlterField(
            model_name='realisasipusisa',
            name='realisasi_tahun',
            field=models.IntegerField(default=2025, verbose_name='Tahun'),
        ),
        migrations.AlterField(
            model_name='rencanapu',
            name='rencana_tahun',
            field=models.IntegerField(default=2025, verbose_name='Tahun'),
        ),
        migrations.AlterField(
            model_name='rencanapuposting',
            name='posting_tahun',
            field=models.IntegerField(default=2025, verbose_name='Tahun'),
        ),
        migrations.AlterField(
            model_name='rencanapupostingsisa',
            name='posting_tahun',
            field=models.IntegerField(default=2025, verbose_name='Tahun'),
        ),
        migrations.AlterField(
            model_name='rencanapusisa',
            name='rencana_tahun',
            field=models.IntegerField(default=2025, verbose_name='Tahun'),
        ),
    ]
