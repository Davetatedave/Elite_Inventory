# Generated by Django 4.2.7 on 2024-01-29 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping_tracker", "0002_alter_deviceattributes_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="devices",
            name="imei",
            field=models.BigIntegerField(unique=True, verbose_name="IMEI"),
        ),
        migrations.AlterField(
            model_name="historicaldevices",
            name="imei",
            field=models.BigIntegerField(db_index=True, verbose_name="IMEI"),
        ),
    ]