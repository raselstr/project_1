# Generated by Django 4.2.11 on 2024-07-25 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dana', '0004_remove_subkegiatan_sub_dana_and_more'),
        ('penerimaan', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='penerimaan',
            name='penerimaan_dana',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dana.subkegiatan', verbose_name='Dana'),
        ),
    ]