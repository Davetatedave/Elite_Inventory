# Generated by Django 4.2.7 on 2023-11-16 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping_tracker", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="tracking", name="id",),
        migrations.RemoveField(model_name="tracking", name="state",),
        migrations.AddField(
            model_name="tracking",
            name="shipper",
            field=models.CharField(default="DHL", max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="tracking",
            name="Arrival_Status",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="tracking",
            name="Expected_Arrival",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="tracking",
            name="Shipping_Status",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="tracking",
            name="date_creation",
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name="tracking",
            name="date_shipping",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="tracking",
            name="order_id",
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="tracking",
            name="tracking_number",
            field=models.CharField(max_length=20),
        ),
    ]
