# Generated by Django 4.2.11 on 2024-09-04 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opd', '0006_alter_pejabat_pejabat_sub'),
    ]

    operations = [
        migrations.AddField(
            model_name='pejabat',
            name='pejabat_foto',
            field=models.ImageField(blank=True, null=True, upload_to='kop_fotos/', verbose_name='Foto Pejabat'),
        ),
        migrations.AddField(
            model_name='pejabat',
            name='pejabat_lokasi',
            field=models.CharField(default='Kisaran', max_length=50, verbose_name='Nama Lokasi'),
            preserve_default=False,
        ),
    ]
