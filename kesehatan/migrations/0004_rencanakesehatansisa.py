# Generated by Django 4.2.11 on 2024-11-08 02:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kesehatan', '0003_alter_realisasikesehatan_realisasi_output'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rencanakesehatansisa',
            fields=[
                ('rencanakesehatan_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='kesehatan.rencanakesehatan')),
            ],
            options={
                'verbose_name': 'Rencana Kesehatan Sisa',
                'verbose_name_plural': 'Rencana Kesehatan Sisa',
                'db_table': 'rencanakesehatansisa',
                'ordering': ['rencana_tahun'],
            },
            bases=('kesehatan.rencanakesehatan',),
        ),
    ]