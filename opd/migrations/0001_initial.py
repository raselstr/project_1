# Generated by Django 4.2.11 on 2024-07-12 08:42

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Opd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kode_opd', models.CharField(error_messages={'unique': 'Data, nilai ini sudah ada dalam database.'}, max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='Data yang diinput harus berupa angka', regex='^[0-9]+$')], verbose_name='Kode OPD')),
                ('nama_opd', models.CharField(error_messages={'unique': 'Maaf, nilai ini sudah ada dalam database.'}, max_length=100, unique=True, validators=[django.core.validators.MinLengthValidator(limit_value=2, message='Data yang diinput minimal 2 karakter')], verbose_name='Nama OPD')),
            ],
        ),
        migrations.CreateModel(
            name='Subopd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_nama', models.CharField(max_length=200, verbose_name='Nama Sub Opd')),
                ('sub_opd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd.opd', verbose_name='Sub Opd')),
            ],
        ),
    ]
