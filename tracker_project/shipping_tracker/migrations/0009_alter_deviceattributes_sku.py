# Generated by Django 4.2.7 on 2024-01-04 16:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shipping_tracker", "0008_deviceattributes_devices"),
    ]

    operations = [
        migrations.AlterField(
            model_name="deviceattributes",
            name="sku",
            field=models.CharField(
                max_length=20, primary_key=True, serialize=False, verbose_name="SKU"
            ),
        ),
    ]
