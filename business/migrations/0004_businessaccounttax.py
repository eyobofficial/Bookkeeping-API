# Generated by Django 3.2.7 on 2021-10-15 11:40

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0003_auto_20210724_2103'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessAccountTax',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('tax_identification_number', models.CharField(blank=True, help_text='Unique TAX identification number issued by the government.', max_length=100, null=True)),
                ('percentage', models.DecimalField(decimal_places=2, help_text='The percentage to be deducted.', max_digits=5)),
                ('active', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taxes', to='business.businessaccount')),
            ],
            options={
                'verbose_name': 'Business Account Tax',
                'verbose_name_plural': 'Business Account Taxes',
            },
        ),
    ]