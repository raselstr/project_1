# Generated by Django 4.2.11 on 2024-08-12 13:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dankel', '0015_realisasidankel_realisasidankel_idrencana'),
    ]

    operations = [
        migrations.AddField(
            model_name='realisasidankelsisa',
            name='realisasidankelsisa_idrencana',
            field=models.IntegerField(default=1, editable=False, verbose_name='Id Rencana'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='realisasidankel',
            name='realisasidankel_idrencana',
            field=models.IntegerField(editable=False, verbose_name='Id Rencana'),
        ),
        migrations.AlterField(
            model_name='realisasidankelsisa',
            name='realisasidankelsisa_rencana',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dankel.rencdankeljadwalsisa', verbose_name='Kegiatan'),
        ),
    ]