# Generated by Django 4.2.11 on 2024-06-19 09:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dana', '0008_subrinc_subrinc_slug'),
        ('dausg', '0008_dankelsub_dankelsub_satuan'),
    ]

    operations = [
        migrations.CreateModel(
            name='DausgkesehatanKeg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dausgkesehatankeg_nama', models.CharField(max_length=200, verbose_name='Kegiatan DAUSG kesehatan')),
            ],
        ),
        migrations.CreateModel(
            name='DausgpendidikanKeg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dausgpendidikankeg_nama', models.CharField(max_length=200, verbose_name='Kegiatan DAUSG Pendidikan')),
            ],
        ),
        migrations.CreateModel(
            name='DausgpuKeg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dausgpukeg_nama', models.CharField(max_length=200, verbose_name='Kegiatan DAUSG Pekerjaan Umum')),
            ],
        ),
        migrations.AlterField(
            model_name='dankelkeg',
            name='dankelkeg_nama',
            field=models.CharField(max_length=200, verbose_name='Kegiatan Dana Kelurahan'),
        ),
        migrations.AlterField(
            model_name='dankelkeg',
            name='dankelkeg_prog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dankelkegs', to='dausg.dankelprog', verbose_name='Program Dana Kelurahan'),
        ),
        migrations.AlterField(
            model_name='dankelprog',
            name='dankel_prog',
            field=models.CharField(max_length=200, verbose_name='Program Dana Kelurahan'),
        ),
        migrations.AlterField(
            model_name='dankelsub',
            name='dankelsub_keg',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dankelsubs', to='dausg.dankelkeg', verbose_name='Kegiatan Dana Kelurahan'),
        ),
        migrations.AlterField(
            model_name='dankelsub',
            name='dankelsub_nama',
            field=models.CharField(max_length=200, verbose_name='Sub Kegiatan Dana Kelurahan'),
        ),
        migrations.CreateModel(
            name='Dausgpusub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dausgpusub_nama', models.CharField(max_length=200, verbose_name='Sub Kegiatan DAUSG Pekerjaan Umum')),
                ('dausgpusub_satuan', models.CharField(max_length=200, verbose_name='Satuan')),
                ('dausgpusub_keg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dausgpusubs', to='dausg.dausgpukeg', verbose_name='Kegiatan DAUSG Pekerjaan Umum')),
            ],
        ),
        migrations.CreateModel(
            name='DausgpuProg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dausgpu_prog', models.CharField(max_length=200, verbose_name='Program DAUSG Pekerjaan Umum')),
                ('dausgpu_dana', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dana.dana', verbose_name='Dana')),
                ('dausgpu_subrinc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dana.subrinc', verbose_name='Sub Rincian Dana')),
            ],
        ),
        migrations.AddField(
            model_name='dausgpukeg',
            name='dausgpukeg_prog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dausgpukegs', to='dausg.dausgpuprog', verbose_name='Program DAUSG Pekerjaan Umum'),
        ),
        migrations.CreateModel(
            name='Dausgpendidikansub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dausgpendidikansub_nama', models.CharField(max_length=200, verbose_name='Sub Kegiatan DAUSG Pendidikan')),
                ('dausgpendidikansub_satuan', models.CharField(max_length=200, verbose_name='Satuan')),
                ('dausgpendidikansub_keg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dausgpendidikansubs', to='dausg.dausgpendidikankeg', verbose_name='Kegiatan DAUSG Pendidikan')),
            ],
        ),
        migrations.CreateModel(
            name='DausgpendidikanProg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dausgpendidikan_prog', models.CharField(max_length=200, verbose_name='Program DAUSG Pendidikan')),
                ('dausgpendidikan_dana', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dana.dana', verbose_name='Dana')),
                ('dausgpendidikan_subrinc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dana.subrinc', verbose_name='Sub Rincian Dana')),
            ],
        ),
        migrations.AddField(
            model_name='dausgpendidikankeg',
            name='dausgpendidikankeg_prog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dausgpendidikankegs', to='dausg.dausgpendidikanprog', verbose_name='Program DAUSG Pendidikan'),
        ),
        migrations.CreateModel(
            name='Dausgkesehatansub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dausgkesehatansub_nama', models.CharField(max_length=200, verbose_name='Sub Kegiatan DAUSG kesehatan')),
                ('dausgkesehatansub_satuan', models.CharField(max_length=200, verbose_name='Satuan')),
                ('dausgkesehatansub_keg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dausgkesehatansubs', to='dausg.dausgkesehatankeg', verbose_name='Kegiatan DAUSG kesehatan')),
            ],
        ),
        migrations.CreateModel(
            name='DausgkesehatanProg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dausgkesehatan_prog', models.CharField(max_length=200, verbose_name='Program DAUSG kesehatan')),
                ('dausgkesehatan_dana', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dana.dana', verbose_name='Dana')),
                ('dausgkesehatan_subrinc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dana.subrinc', verbose_name='Sub Rincian Dana')),
            ],
        ),
        migrations.AddField(
            model_name='dausgkesehatankeg',
            name='dausgkesehatankeg_prog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dausgkesehatankegs', to='dausg.dausgkesehatanprog', verbose_name='Program DAUSG kesehatan'),
        ),
    ]