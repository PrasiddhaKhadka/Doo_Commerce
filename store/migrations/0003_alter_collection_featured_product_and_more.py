# Generated by Django 5.2.3 on 2025-06-23 23:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_remove_customer_address_alter_cartitem_cart_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='featured_product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='store.product'),
        ),
        migrations.AlterField(
            model_name='product',
            name='collection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='store.collection'),
        ),
    ]
