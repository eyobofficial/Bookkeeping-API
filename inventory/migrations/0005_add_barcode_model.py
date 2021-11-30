# Generated by Django 3.2.7 on 2021-11-29 20:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0005_add_tax_identification_number'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0004_alter_stock_unit'),
    ]

    operations = [
        migrations.CreateModel(
            name='Barcode',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=255, unique=True)),
                ('product_name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, help_text='Short description about the product.')),
                ('product_photo', models.ImageField(blank=True, null=True, upload_to='barcodes')),
                ('barcode_photo', models.ImageField(blank=True, null=True, upload_to='barcodes')),
                ('created_by_api', models.BooleanField(default=False, help_text='Barcode is created by during API calls by a Business Account.')),
                ('verified', models.BooleanField(default=False, help_text='Verify the entered barcode matches with the number in the uploaded photo.')),
                ('archived', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('business_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='barcodes', to='business.businessaccount')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_barcodes', to=settings.AUTH_USER_MODEL)),
                ('verified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_barcodes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddField(
            model_name='stock',
            name='barcode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stocks', to='inventory.barcode'),
        ),
    ]
