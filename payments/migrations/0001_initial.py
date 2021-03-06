# Generated by Django 3.1.7 on 2021-06-30 09:10

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('mode_of_payment', models.CharField(choices=[('CASH', 'Cash'), ('BANK', 'Bank Transfer'), ('CARD', 'Card Transfer'), ('CREDIT', 'Pay Later')], max_length=10)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='PENDING', max_length=10)),
                ('pay_later_date', models.DateField(blank=True, help_text='Required if mode of payment is `CREDIT`.', null=True)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='payments/receipts/')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Payment transaction created date and time.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Payment transaction last updated date and time.')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='orders.order')),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
                'ordering': ('-created_at',),
            },
        ),
    ]
