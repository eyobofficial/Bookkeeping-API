# Generated by Django 3.1.7 on 2021-06-08 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_auto_20210608_0018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='description',
            field=models.TextField(blank=True, help_text='Required for `CUSTOM` order types to describe the sold items.', null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='pay_later_date',
            field=models.DateField(blank=True, help_text='Required if mode of payment is `CREDIT`.', null=True),
        ),
    ]
