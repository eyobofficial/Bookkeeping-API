# Generated by Django 3.1.7 on 2021-05-30 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0011_auto_20210520_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesstype',
            name='icon',
            field=models.ImageField(blank=True, null=True, upload_to='business/icons/'),
        ),
    ]