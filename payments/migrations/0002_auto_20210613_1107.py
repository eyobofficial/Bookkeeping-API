# Generated by Django 3.1.7 on 2021-06-13 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='pay_later_date',
            field=models.DateField(blank=True, help_text='Required if mode of payment is `CREDIT`.', null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='orders/receipts/'),
        ),
    ]
