# Generated by Django 4.2.11 on 2024-06-19 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('opd', '0008_alter_subopd_sub_opd'),
        ('dankel', '0003_alter_rencdankelsisa_rencdankelsisa_rencana'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rencdankel',
            name='rencdankel_opd',
        ),
        migrations.AddField(
            model_name='rencdankel',
            name='rencdankel_subopd',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='opd.subopd', verbose_name='Sub Opd'),
            preserve_default=False,
        ),
    ]