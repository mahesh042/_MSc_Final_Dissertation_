# Generated by Django 4.0.3 on 2022-04-09 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dockstation',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=16, max_digits=22, null=True),
        ),
        migrations.AlterField(
            model_name='dockstation',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=16, max_digits=22, null=True),
        ),
    ]
