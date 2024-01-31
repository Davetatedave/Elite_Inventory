# Generated by Django 4.2.7 on 2024-01-31 14:42

from django.db import migrations, models
import django.db.models.deletion
import phone_field.models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping_tracker", "0003_alter_devices_imei_alter_historicaldevices_imei"),
    ]

    operations = [
        migrations.CreateModel(
            name="address",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("street", models.CharField(max_length=20, verbose_name="Street")),
                ("street2", models.CharField(max_length=20, verbose_name="Street2")),
                ("city", models.CharField(max_length=20, verbose_name="City")),
                ("state", models.CharField(max_length=20, verbose_name="State")),
                ("postalCode", models.CharField(max_length=20, verbose_name="Zip")),
                (
                    "phone",
                    phone_field.models.PhoneField(
                        blank=True, help_text="Contact phone number", max_length=31
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="country",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=20, verbose_name="Country")),
                ("code", models.CharField(max_length=20, verbose_name="Country Code")),
            ],
        ),
        migrations.RemoveField(
            model_name="historicalsalesorderitems", name="currencies",
        ),
        migrations.RemoveField(
            model_name="historicalsalesorderitems", name="date_added",
        ),
        migrations.RemoveField(model_name="salesorderitems", name="currencies",),
        migrations.RemoveField(model_name="salesorderitems", name="date_added",),
        migrations.AddField(
            model_name="salesorders",
            name="state",
            field=models.CharField(
                default="Open", max_length=20, null=True, verbose_name="State"
            ),
        ),
        migrations.CreateModel(
            name="customer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=20, verbose_name="Customer Name")),
                ("contact", models.CharField(max_length=20, verbose_name="Contact")),
                ("email", models.CharField(max_length=20, verbose_name="Email")),
                (
                    "phone",
                    phone_field.models.PhoneField(
                        blank=True, help_text="Contact phone number", max_length=31
                    ),
                ),
                (
                    "channel",
                    models.CharField(max_length=20, null=True, verbose_name="Channel"),
                ),
                (
                    "billing_address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="billing_customers",
                        to="shipping_tracker.address",
                        verbose_name="Billing Address",
                    ),
                ),
                (
                    "currency",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="shipping_tracker.currencies",
                        verbose_name="Currency",
                    ),
                ),
                (
                    "shipping_address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="shipping_customers",
                        to="shipping_tracker.address",
                        verbose_name="Shipping Address",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="address",
            name="country",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="shipping_tracker.country",
                verbose_name="Country",
            ),
        ),
        migrations.AddField(
            model_name="salesorders",
            name="customer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="shipping_tracker.customer",
                verbose_name="Customer",
            ),
        ),
    ]
