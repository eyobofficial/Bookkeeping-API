# Generated by Django 3.1.7 on 2021-05-20 20:51

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_auto_20210520_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None),
            preserve_default=False,
        ),
    ]