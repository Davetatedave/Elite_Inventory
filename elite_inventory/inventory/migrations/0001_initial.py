# Generated by Django 4.2.7 on 2024-02-16 12:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
                ("name", models.CharField(max_length=40, verbose_name="Name")),
                ("street", models.CharField(max_length=50, verbose_name="Street")),
                ("street2", models.CharField(max_length=20, verbose_name="Street2")),
                ("city", models.CharField(max_length=20, verbose_name="City")),
                ("state", models.CharField(max_length=20, verbose_name="State")),
                ("postalCode", models.CharField(max_length=20, verbose_name="Zip")),
                ("phone", models.CharField(max_length=20, verbose_name="Phone")),
                ("country", models.CharField(max_length=20, verbose_name="Country")),
            ],
        ),
        migrations.CreateModel(
            name="currencies",
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
                (
                    "name",
                    models.CharField(
                        max_length=20, unique=True, verbose_name="Currency Name"
                    ),
                ),
                ("symbol", models.CharField(max_length=20, verbose_name="Symbol")),
                (
                    "default_rate",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="Rate"
                    ),
                ),
            ],
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
                (
                    "phone",
                    models.CharField(max_length=20, null=True, verbose_name="Phone"),
                ),
                ("email", models.CharField(max_length=20, verbose_name="Email")),
                (
                    "channel",
                    models.CharField(max_length=20, null=True, verbose_name="Channel"),
                ),
                (
                    "billing_address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="billing_customers",
                        to="inventory.address",
                        verbose_name="Billing Address",
                    ),
                ),
                (
                    "currency",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="inventory.currencies",
                        verbose_name="Currency",
                    ),
                ),
                (
                    "shipping_address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="shipping_customers",
                        to="inventory.address",
                        verbose_name="Shipping Address",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="deviceAttributes",
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
                (
                    "sku",
                    models.CharField(max_length=20, unique=True, verbose_name="SKU"),
                ),
                (
                    "manufacturer",
                    models.CharField(max_length=20, verbose_name="Manufacturer"),
                ),
                ("model", models.CharField(max_length=40, verbose_name="Model")),
                ("color", models.CharField(max_length=20, verbose_name="Color")),
                ("capacity", models.CharField(max_length=20, verbose_name="Capacity")),
                (
                    "carrier",
                    models.CharField(blank=True, max_length=20, verbose_name="Carrier"),
                ),
                ("grade", models.CharField(max_length=20, verbose_name="Grade")),
            ],
        ),
        migrations.CreateModel(
            name="devices",
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
                ("imei", models.BigIntegerField(unique=True, verbose_name="IMEI")),
                ("battery", models.IntegerField(null=True, verbose_name="Battery")),
                (
                    "date_added",
                    models.DateField(auto_now_add=True, verbose_name="Date Added"),
                ),
                (
                    "date_tested",
                    models.DateField(null=True, verbose_name="Date Tested"),
                ),
                (
                    "working",
                    models.BooleanField(
                        default=None, null=True, verbose_name="Working"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="deviceStatus",
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
                (
                    "status",
                    models.CharField(
                        default="Unvailable",
                        max_length=20,
                        verbose_name="Device Status",
                    ),
                ),
                (
                    "sellable",
                    models.BooleanField(default=False, verbose_name="Sellable"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="salesOrders",
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
                ("so", models.IntegerField(unique=True, verbose_name="SO")),
                (
                    "date_created",
                    models.DateField(auto_now_add=True, verbose_name="Date Added"),
                ),
                (
                    "date_shipped",
                    models.DateField(null=True, verbose_name="Date Shipped"),
                ),
                (
                    "shipped_by",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Shipped By"
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        default="Open", max_length=20, null=True, verbose_name="State"
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="inventory.customer",
                        verbose_name="Customer",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="trackingDb",
            fields=[
                (
                    "order_id",
                    models.IntegerField(
                        primary_key=True, serialize=False, verbose_name="Order ID"
                    ),
                ),
                ("ol_state", models.IntegerField(verbose_name="State")),
                ("shipper", models.CharField(max_length=20, verbose_name="Shipper")),
                (
                    "tracking_number",
                    models.CharField(max_length=20, verbose_name="Tracking Number"),
                ),
                (
                    "date_creation",
                    models.DateTimeField(null=True, verbose_name="Creation Date"),
                ),
                (
                    "date_shipping",
                    models.DateField(null=True, verbose_name="Shipping Date"),
                ),
                (
                    "Shipping_Status",
                    models.CharField(max_length=20, verbose_name="Shipping Status"),
                ),
                (
                    "Expected_Arrival",
                    models.DateField(null=True, verbose_name="Expected Arrival"),
                ),
                (
                    "Arrival_Status",
                    models.CharField(max_length=20, verbose_name="Arrival Status"),
                ),
                ("history", models.JSONField(verbose_name="History")),
            ],
        ),
        migrations.CreateModel(
            name="warehouse",
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
                (
                    "name",
                    models.CharField(max_length=20, verbose_name="Warehouse Name"),
                ),
                (
                    "address",
                    models.CharField(max_length=20, null=True, verbose_name="Address"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="suppliers",
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
                (
                    "name",
                    models.CharField(
                        max_length=20, unique=True, verbose_name="Supplier Name"
                    ),
                ),
                ("address", models.CharField(max_length=20, verbose_name="Address")),
                ("contact", models.CharField(max_length=20, verbose_name="Contact")),
                ("email", models.CharField(max_length=20, verbose_name="Email")),
                (
                    "currency",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="inventory.currencies",
                        verbose_name="Currency",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="shipment",
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
                (
                    "tracking_number",
                    models.CharField(max_length=20, verbose_name="Tracking Number"),
                ),
                (
                    "tracking_url",
                    models.URLField(
                        max_length=500, null=True, verbose_name="Tracking URL"
                    ),
                ),
                (
                    "public_tracking_url",
                    models.URLField(
                        max_length=500, null=True, verbose_name="Public Tracking URL"
                    ),
                ),
                ("shipper", models.CharField(max_length=20, verbose_name="Shipper")),
                (
                    "date_shipped",
                    models.DateField(null=True, verbose_name="Date Shipped"),
                ),
                (
                    "date_delivered",
                    models.DateField(null=True, verbose_name="Date Delivered"),
                ),
                (
                    "delivered_by",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Delivered By"
                    ),
                ),
                (
                    "shipping_cost",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=5,
                        null=True,
                        verbose_name="Shipping Cost",
                    ),
                ),
                (
                    "label_blob_name",
                    models.CharField(
                        max_length=500, null=True, verbose_name="Shipping Label"
                    ),
                ),
                (
                    "so",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="inventory.salesorders",
                        verbose_name="SO",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="salesorders",
            name="warehouse",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="inventory.warehouse",
                verbose_name="Warehouse",
            ),
        ),
        migrations.CreateModel(
            name="salesOrderItems",
            fields=[
                ("item", models.AutoField(primary_key=True, serialize=False)),
                (
                    "description",
                    models.CharField(
                        max_length=80, null=True, verbose_name="Description"
                    ),
                ),
                ("quantity", models.IntegerField(verbose_name="Quantity")),
                (
                    "unit_cost",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="Unit Cost"
                    ),
                ),
                (
                    "salesorder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="inventory.salesorders",
                        verbose_name="SO",
                    ),
                ),
                (
                    "sku",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="inventory.deviceattributes",
                        verbose_name="SKU",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="purchaseOrders",
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
                ("po", models.CharField(max_length=20, verbose_name="PO")),
                (
                    "date_added",
                    models.DateField(auto_now_add=True, verbose_name="Date Added"),
                ),
                (
                    "date_received",
                    models.DateField(null=True, verbose_name="Date Received"),
                ),
                (
                    "received_by",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Received By"
                    ),
                ),
                (
                    "warehouse",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="inventory.warehouse",
                        verbose_name="Warehouse",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="purchaseOrderItems",
            fields=[
                ("item", models.AutoField(primary_key=True, serialize=False)),
                ("quantity", models.IntegerField(verbose_name="Quantity")),
                (
                    "unit_cost",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="Unit Cost"
                    ),
                ),
                (
                    "date_added",
                    models.DateField(auto_now_add=True, verbose_name="Date Added"),
                ),
                (
                    "currencies",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="inventory.currencies",
                        verbose_name="Currency",
                    ),
                ),
                (
                    "po",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inventory.purchaseorders",
                        verbose_name="PO",
                    ),
                ),
                (
                    "sku",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="inventory.deviceattributes",
                        verbose_name="SKU",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="inventory.suppliers",
                        verbose_name="Supplier",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalpurchaseOrders",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("po", models.CharField(max_length=20, verbose_name="PO")),
                (
                    "date_added",
                    models.DateField(
                        blank=True, editable=False, verbose_name="Date Added"
                    ),
                ),
                (
                    "date_received",
                    models.DateField(null=True, verbose_name="Date Received"),
                ),
                (
                    "received_by",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Received By"
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "warehouse",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.warehouse",
                        verbose_name="Warehouse",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical purchase orders",
                "verbose_name_plural": "historical purchase orderss",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalpurchaseOrderItems",
            fields=[
                ("item", models.IntegerField(blank=True, db_index=True)),
                ("quantity", models.IntegerField(verbose_name="Quantity")),
                (
                    "unit_cost",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="Unit Cost"
                    ),
                ),
                (
                    "date_added",
                    models.DateField(
                        blank=True, editable=False, verbose_name="Date Added"
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "currencies",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.currencies",
                        verbose_name="Currency",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "po",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.purchaseorders",
                        verbose_name="PO",
                    ),
                ),
                (
                    "sku",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.deviceattributes",
                        verbose_name="SKU",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.suppliers",
                        verbose_name="Supplier",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical purchase order items",
                "verbose_name_plural": "historical purchase order itemss",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="Historicaldevices",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("imei", models.BigIntegerField(db_index=True, verbose_name="IMEI")),
                ("battery", models.IntegerField(null=True, verbose_name="Battery")),
                (
                    "date_added",
                    models.DateField(
                        blank=True, editable=False, verbose_name="Date Added"
                    ),
                ),
                (
                    "date_tested",
                    models.DateField(null=True, verbose_name="Date Tested"),
                ),
                (
                    "working",
                    models.BooleanField(
                        default=None, null=True, verbose_name="Working"
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "deviceStatus",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        default=1,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.devicestatus",
                        verbose_name="Device Status",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "po",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.purchaseorders",
                        verbose_name="PO",
                    ),
                ),
                (
                    "sku",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.deviceattributes",
                        verbose_name="SKU",
                    ),
                ),
                (
                    "so",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.salesorders",
                        verbose_name="SO",
                    ),
                ),
                (
                    "warehouse",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.warehouse",
                        verbose_name="Warehouse",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical devices",
                "verbose_name_plural": "historical devicess",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalBackMarketListing",
            fields=[
                ("listing_id", models.IntegerField(db_index=True)),
                ("bm_sku", models.CharField(max_length=100, verbose_name="BM SKU")),
                ("title", models.CharField(max_length=255)),
                (
                    "price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "min_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("quantity", models.IntegerField(blank=True, null=True)),
                ("backmarket_id", models.IntegerField()),
                ("product_id", models.UUIDField()),
                (
                    "max_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sku",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.deviceattributes",
                        verbose_name="SKU",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical back market listing",
                "verbose_name_plural": "historical back market listings",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="faults",
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
                ("fault", models.CharField(max_length=20, verbose_name="Fault")),
                (
                    "repaired",
                    models.BooleanField(default=False, verbose_name="Repaired"),
                ),
                (
                    "date_repaired",
                    models.DateField(null=True, verbose_name="Date Repaired"),
                ),
                (
                    "repaired_by",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Repaired By"
                    ),
                ),
                (
                    "repair_cost",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=5,
                        null=True,
                        verbose_name="Repair Cost",
                    ),
                ),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inventory.devices",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="devices",
            name="deviceStatus",
            field=models.ForeignKey(
                default=1,
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                to="inventory.devicestatus",
                verbose_name="Device Status",
            ),
        ),
        migrations.AddField(
            model_name="devices",
            name="po",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="inventory.purchaseorders",
                verbose_name="PO",
            ),
        ),
        migrations.AddField(
            model_name="devices",
            name="sku",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="inventory.deviceattributes",
                verbose_name="SKU",
            ),
        ),
        migrations.AddField(
            model_name="devices",
            name="so",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="inventory.salesorders",
                verbose_name="SO",
            ),
        ),
        migrations.AddField(
            model_name="devices",
            name="warehouse",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="inventory.warehouse",
                verbose_name="Warehouse",
            ),
        ),
        migrations.CreateModel(
            name="BackMarketListing",
            fields=[
                (
                    "listing_id",
                    models.IntegerField(primary_key=True, serialize=False, unique=True),
                ),
                ("bm_sku", models.CharField(max_length=100, verbose_name="BM SKU")),
                ("title", models.CharField(max_length=255)),
                (
                    "price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "min_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("quantity", models.IntegerField(blank=True, null=True)),
                ("backmarket_id", models.IntegerField()),
                ("product_id", models.UUIDField()),
                (
                    "max_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "sku",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="inventory.deviceattributes",
                        verbose_name="SKU",
                    ),
                ),
            ],
        ),
    ]
