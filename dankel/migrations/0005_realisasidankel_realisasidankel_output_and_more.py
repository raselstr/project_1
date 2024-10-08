# Generated by Django 4.2.11 on 2024-08-02 09:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dankel', '0004_realisasidankelsisa'),
    ]

    operations = [
        migrations.AddField(
            model_name='realisasidankel',
            name='realisasidankel_output',
            field=models.CharField(default=1, max_length=100, verbose_name='Output'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='realisasidankel',
            name='realisasidankel_rencana',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rencanas', to='dankel.rencdankel', verbose_name='Kegiatan'),
        ),
    ]
