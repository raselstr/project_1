# Generated by Django 4.2.11 on 2024-11-08 02:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kesehatan', '0004_rencanakesehatansisa'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rencanakesehatansisa',
            options={'ordering': ['rencana_tahun']},
        ),
    ]