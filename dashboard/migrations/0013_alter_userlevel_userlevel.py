# Generated by Django 4.2.11 on 2024-05-30 02:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_userlevel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlevel',
            name='userlevel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.level'),
        ),
    ]