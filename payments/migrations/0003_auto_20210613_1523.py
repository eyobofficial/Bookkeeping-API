# Generated by Django 3.1.7 on 2021-06-13 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_auto_20210613_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, help_text='Payment transaction last updated date and time.'),
        ),
    ]