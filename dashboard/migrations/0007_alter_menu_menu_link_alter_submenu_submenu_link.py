# Generated by Django 4.2.11 on 2024-05-27 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_alter_menu_menu_icon_alter_submenu_submenu_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='menu_link',
            field=models.CharField(blank=True, max_length=25),
        ),
        migrations.AlterField(
            model_name='submenu',
            name='submenu_link',
            field=models.CharField(blank=True, max_length=25),
        ),
    ]