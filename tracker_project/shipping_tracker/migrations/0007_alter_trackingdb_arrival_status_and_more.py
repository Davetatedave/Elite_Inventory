# Generated by Django 4.2.7 on 2023-12-21 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping_tracker", "0006_alter_trackingdb_date_creation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trackingdb",
            name="Arrival_Status",
            field=models.CharField(max_length=20, verbose_name="Arrival Status"),
        ),
        migrations.AlterField(
            model_name="trackingdb",
            name="Expected_Arrival",
            field=models.DateField(null=True, verbose_name="Expected Arrival"),
        ),
        migrations.AlterField(
            model_name="trackingdb",
            name="Shipping_Status",
            field=models.CharField(max_length=20, verbose_name="Shipping Status"),
        ),
        migrations.AlterField(
            model_name="trackingdb",
            name="date_creation",
            field=models.DateTimeField(null=True, verbose_name="Creation Date"),
        ),
        migrations.AlterField(
            model_name="trackingdb",
            name="date_shipping",
            field=models.DateField(null=True, verbose_name="Shipping Date"),
        ),
        migrations.AlterField(
            model_name="trackingdb",
            name="history",
            field=models.JSONField(verbose_name="History"),
        ),
        migrations.AlterField(
            model_name="trackingdb",
            name="ol_state",
            field=models.IntegerField(verbose_name="State"),
        ),
        migrations.AlterField(
            model_name="trackingdb",
            name="order_id",
            field=models.IntegerField(
                primary_key=True, serialize=False, verbose_name="Order ID"
            ),
        ),
        migrations.AlterField(
            model_name="trackingdb",
            name="shipper",
            field=models.CharField(max_length=20, verbose_name="Shipper"),
        ),
        migrations.AlterField(
            model_name="trackingdb",
            name="tracking_number",
            field=models.CharField(max_length=20, verbose_name="Tracking Number"),
        ),
    ]
