# Generated by Django 4.2.11 on 2024-08-20 07:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('opd', '0005_alter_pejabat_pejabat_sub'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pejabat',
            name='pejabat_sub',
            field=models.OneToOneField(error_messages='OPD ini sudah memiliki Pejabat', on_delete=django.db.models.deletion.CASCADE, to='opd.subopd', verbose_name='Nama OPD'),
        ),
    ]
