# Generated by Django 3.1.7 on 2021-06-09 01:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20210607_1451'),
        ('orders', '0009_auto_20210609_0135'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='orderitem',
            unique_together={('order', 'item')},
        ),
    ]