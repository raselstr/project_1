# Generated by Django 4.2.11 on 2024-11-08 09:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pendidikan', '0015_alter_rencanaposting_table_rencanapostingsisa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rencanapostingsisa',
            name='posting_rencanaid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pendidikan.rencanasisa', verbose_name='Id Rencana'),
        ),
    ]