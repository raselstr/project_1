# Generated by Django 4.2.11 on 2024-05-26 09:28

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('opd', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('biography', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('website', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='opd',
            name='kode_opd',
            field=models.CharField(max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='Kode OPD harus berupa angka', regex='^[0-9]+$')]),
        ),
        migrations.AlterField(
            model_name='opd',
            name='nama_opd',
            field=models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(limit_value=3, message='Gak boleh lebih dari 3')]),
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('publication_date', models.DateField()),
                ('isbn', models.CharField(max_length=13, unique=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd.author')),
                ('publisher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opd.publisher')),
            ],
        ),
    ]