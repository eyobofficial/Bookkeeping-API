# Generated by Django 3.1.7 on 2021-09-02 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='custom_cost',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='A total price offer for custom order.', max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
    ]
