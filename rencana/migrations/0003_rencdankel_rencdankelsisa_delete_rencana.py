# Generated by Django 4.2.11 on 2024-06-13 14:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dausg', '0008_dankelsub_dankelsub_satuan'),
        ('opd', '0006_alter_opd_kode_opd_alter_opd_nama_opd'),
        ('rencana', '0002_rencana_rencana_tahun'),
    ]

    operations = [
        migrations.CreateModel(
            name='RencDankel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rencdankel_tahun', models.IntegerField(default=2024, verbose_name='Tahun')),
                ('rencdankel_pagu', models.DecimalField(decimal_places=2, default=0, max_digits=17, verbose_name='Pagu Anggaran')),
                ('rencdankel_output', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Output')),
                ('rencdankel_ket', models.TextField(verbose_name='Keterangan Kegiatan')),
                ('rencdankel_opd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd.opd', verbose_name='Opd')),
                ('rencdankel_sub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dausg.dankelsub', verbose_name='Sub Kegiatan')),
            ],
        ),
        migrations.CreateModel(
            name='RencDankelsisa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rencdankelsisa_tahun', models.IntegerField(default=2024, verbose_name='Tahun')),
                ('rencdankelsisa_pagu', models.DecimalField(decimal_places=2, default=0, max_digits=17, verbose_name='Pagu Anggaran')),
                ('rencdankelsisa_output', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Output')),
                ('rencdankelsisa_ket', models.TextField(verbose_name='Keterangan Kegiatan')),
                ('rencdankelsisa_opd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd.opd', verbose_name='Opd')),
                ('rencdankelsisa_sub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dausg.dankelsub', verbose_name='Sub Kegiatan')),
            ],
        ),
        migrations.DeleteModel(
            name='Rencana',
        ),
    ]