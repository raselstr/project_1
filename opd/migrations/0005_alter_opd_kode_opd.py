# Generated by Django 4.2.11 on 2024-05-29 08:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opd', '0004_alter_opd_kode_opd_alter_opd_nama_opd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opd',
            name='kode_opd',
            field=models.CharField(error_messages={'unique': 'Data, nilai ini sudah ada dalam database.'}, max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='Data yang diinput harus berupa angka', regex='^[0-9]+$')]),
        ),
    ]