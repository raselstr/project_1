# Generated by Django 4.2.11 on 2024-08-07 07:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('opd', '0003_alter_opd_kode_opd'),
        ('dana', '0004_remove_subkegiatan_sub_dana_and_more'),
        ('dausg', '0002_remove_dankelprog_dankel_subrinc_and_more'),
        ('dankel', '0009_alter_rencdankeljadwal_rencdankel_jadwal'),
    ]

    operations = [
        migrations.CreateModel(
            name='RencDankeljadwalsisa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rencdankelsisa_tahun', models.IntegerField(default=2024, verbose_name='Tahun')),
                ('rencdankelsisa_pagu', models.DecimalField(decimal_places=2, default=0, max_digits=17, verbose_name='Pagu Anggaran Sisa')),
                ('rencdankelsisa_output', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Output Sisa')),
                ('rencdankelsisa_ket', models.TextField(blank=True, verbose_name='Keterangan Kegiatan Sisa')),
                ('rencdankelsisa_jadwal', models.IntegerField(choices=[(1, 'Rencana Induk'), (2, 'Rencana Perubahan')], null=True)),
                ('rencdankelsisa_dana', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dana.subkegiatan', verbose_name='Sumber Dana')),
                ('rencdankelsisa_sub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dausg.dankelsub', verbose_name='Sub Kegiatan')),
                ('rencdankelsisa_subopd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd.subopd', verbose_name='Sub Opd')),
            ],
        ),
    ]