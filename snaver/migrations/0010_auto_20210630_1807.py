# Generated by Django 3.2 on 2021-06-30 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snaver', '0009_auto_20210627_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='inflow',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='outflow',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=11),
        ),
    ]
