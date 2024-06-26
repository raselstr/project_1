# Generated by Django 4.2.11 on 2024-06-12 05:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opd', '0005_alter_opd_kode_opd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opd',
            name='kode_opd',
            field=models.CharField(error_messages={'unique': 'Data, nilai ini sudah ada dalam database.'}, max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='Data yang diinput harus berupa angka', regex='^[0-9]+$')], verbose_name='Kode OPD'),
        ),
        migrations.AlterField(
            model_name='opd',
            name='nama_opd',
            field=models.CharField(error_messages={'unique': 'Maaf, nilai ini sudah ada dalam database.'}, max_length=100, unique=True, validators=[django.core.validators.MinLengthValidator(limit_value=2, message='Data yang diinput minimal 2 karakter')], verbose_name='Nama OPD'),
        ),
    ]
