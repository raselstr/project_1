# Generated by Django 4.2.11 on 2024-06-12 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('penerimaan', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='penerimaan',
            name='penerimaan_nilai',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=17, verbose_name='Nilai Uang'),
        ),
    ]