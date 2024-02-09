from django.db import models
from .utils import check_shipping_status
from django.db.models import Case, When, Value
from simple_history.models import HistoricalRecords


# Create your models here.
class trackingDb(models.Model):
    order_id = models.IntegerField(primary_key=True, verbose_name="Order ID")
    ol_state = models.IntegerField(verbose_name="State")
    shipper = models.CharField(max_length=20, verbose_name="Shipper")
    tracking_number = models.CharField(max_length=20, verbose_name="Tracking Number")
    date_creation = models.DateTimeField(null=True, verbose_name="Creation Date")
    date_shipping = models.DateField(null=True, verbose_name="Shipping Date")
    Shipping_Status = models.CharField(max_length=20, verbose_name="Shipping Status")
    Expected_Arrival = models.DateField(null=True, verbose_name="Expected Arrival")
    Arrival_Status = models.CharField(max_length=20, verbose_name="Arrival Status")
    history = models.JSONField(verbose_name="History")

    def status(self):
        return check_shipping_status(self)


class deviceAttributes(models.Model):
    sku = models.CharField(max_length=20, primary_key=True, verbose_name="SKU")
    manufacturer = models.CharField(max_length=20, verbose_name="Manufacturer")
    model = models.CharField(max_length=40, verbose_name="Model")
    color = models.CharField(max_length=20, verbose_name="Color")
    capacity = models.CharField(max_length=20, verbose_name="Capacity")
    carrier = models.CharField(max_length=20, verbose_name="Carrier", blank=True)
    grade = models.CharField(max_length=20, verbose_name="Grade")

    def name(self):
        return f"{self.model} {self.color} {self.capacity} {self.grade}"


class warehouse(models.Model):
    name = models.CharField(
        max_length=20, primary_key=True, verbose_name="Warehouse Name"
    )
    address = models.CharField(max_length=20, verbose_name="Address", null=True)


class deviceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(deviceStatus__id=1)


class deviceStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(
        max_length=20, verbose_name="Device Status", default="Unvailable"
    )
    sellable = models.BooleanField(verbose_name="Sellable", default=False)

    def __str__(self):
        return self.status


class currencies(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="Currency Name")
    symbol = models.CharField(max_length=20, verbose_name="Symbol")
    default_rate = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Rate"
    )

    def __str__(self):
        return self.name


class suppliers(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="Supplier Name")
    address = models.CharField(max_length=20, verbose_name="Address")
    contact = models.CharField(max_length=20, verbose_name="Contact")
    email = models.CharField(max_length=20, verbose_name="Email")
    currency = models.ForeignKey(
        currencies, on_delete=models.SET_NULL, verbose_name="Currency", null=True
    )

    def __str__(self):
        return self.name


class purchaseOrders(models.Model):
    po = models.CharField(max_length=20, verbose_name="PO")

    date_added = models.DateField(verbose_name="Date Added", auto_now_add=True)
    date_received = models.DateField(verbose_name="Date Received", null=True)
    received_by = models.CharField(max_length=20, verbose_name="Received By", null=True)
    warehouse = models.ForeignKey(
        warehouse, on_delete=models.PROTECT, verbose_name="Warehouse", null=True
    )
    history = HistoricalRecords()


class purchaseOrderItems(models.Model):
    item = models.AutoField(primary_key=True)
    po = models.ForeignKey(purchaseOrders, on_delete=models.CASCADE, verbose_name="PO")
    sku = models.ForeignKey(
        deviceAttributes, on_delete=models.PROTECT, verbose_name="SKU"
    )
    quantity = models.IntegerField(verbose_name="Quantity")
    unit_cost = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Unit Cost"
    )
    currencies = models.ForeignKey(
        currencies, on_delete=models.PROTECT, verbose_name="Currency"
    )
    supplier = models.ForeignKey(
        suppliers, on_delete=models.PROTECT, verbose_name="Supplier"
    )
    date_added = models.DateField(verbose_name="Date Added", auto_now_add=True)
    history = HistoricalRecords()


class address(models.Model):
    name = models.CharField(max_length=40, verbose_name="Name")
    street = models.CharField(max_length=50, verbose_name="Street")
    street2 = models.CharField(max_length=20, verbose_name="Street2")
    city = models.CharField(max_length=20, verbose_name="City")
    state = models.CharField(max_length=20, verbose_name="State")
    postalCode = models.CharField(max_length=20, verbose_name="Zip")
    phone = models.CharField(max_length=20, verbose_name="Phone")
    country = models.CharField(max_length=20, verbose_name="Country")


class customer(models.Model):
    name = models.CharField(max_length=20, verbose_name="Customer Name")
    shipping_address = models.ForeignKey(
        address,
        on_delete=models.PROTECT,
        verbose_name="Shipping Address",
        related_name="shipping_customers",
    )
    billing_address = models.ForeignKey(
        address,
        on_delete=models.PROTECT,
        verbose_name="Billing Address",
        related_name="billing_customers",
    )
    contact = models.CharField(max_length=20, verbose_name="Contact")
    phone = models.CharField(max_length=20, verbose_name="Phone", null=True)
    email = models.CharField(max_length=20, verbose_name="Email")
    currency = models.ForeignKey(
        currencies, on_delete=models.SET_NULL, verbose_name="Currency", null=True
    )
    channel = models.CharField(max_length=20, verbose_name="Channel", null=True)

    def __str__(self):
        return self.name


class salesOrders(models.Model):
    so = models.IntegerField(primary_key=True, verbose_name="SO")
    customer = models.ForeignKey(
        customer, on_delete=models.PROTECT, verbose_name="Customer", null=True
    )
    date_created = models.DateField(verbose_name="Date Added", auto_now_add=True)
    date_shipped = models.DateField(verbose_name="Date Shipped", null=True)
    shipped_by = models.CharField(max_length=20, verbose_name="Shipped By", null=True)
    warehouse = models.ForeignKey(
        warehouse, on_delete=models.PROTECT, verbose_name="Warehouse", null=True
    )
    state = models.CharField(
        max_length=20, verbose_name="State", null=True, default="Open"
    )
    # history = HistoricalRecords()


class salesOrderItems(models.Model):
    item = models.AutoField(primary_key=True)
    salesorder = models.ForeignKey(
        salesOrders, on_delete=models.CASCADE, verbose_name="SO", related_name="items"
    )
    sku = models.ForeignKey(
        deviceAttributes, on_delete=models.PROTECT, verbose_name="SKU", null=True
    )
    description = models.CharField(max_length=80, verbose_name="Description", null=True)
    quantity = models.IntegerField(verbose_name="Quantity")
    unit_cost = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Unit Cost"
    )


class shipment(models.Model):
    so = models.ForeignKey(
        salesOrders, on_delete=models.PROTECT, verbose_name="SO", null=True
    )
    tracking_number = models.CharField(max_length=20, verbose_name="Tracking Number")
    tracking_url = models.URLField(
        max_length=500, null=True, verbose_name="Tracking URL"
    )
    shipper = models.CharField(max_length=20, verbose_name="Shipper")
    date_shipped = models.DateField(verbose_name="Date Shipped", null=True)
    date_delivered = models.DateField(verbose_name="Date Delivered", null=True)
    delivered_by = models.CharField(
        max_length=20, verbose_name="Delivered By", null=True
    )
    shipping_cost = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Shipping Cost", null=True
    )
    shipping_label = models.URLField(
        max_length=500, verbose_name="Shipping Label", null=True
    )


class devices(models.Model):
    imei = models.BigIntegerField(unique=True, verbose_name="IMEI")
    sku = models.ForeignKey(
        deviceAttributes, on_delete=models.PROTECT, verbose_name="SKU"
    )
    deviceStatus = models.ForeignKey(
        deviceStatus,
        on_delete=models.SET_DEFAULT,
        verbose_name="Device Status",
        null=True,
        default=2,
    )
    battery = models.IntegerField(verbose_name="Battery", null=True)
    date_added = models.DateField(verbose_name="Date Added", auto_now_add=True)
    date_tested = models.DateField(verbose_name="Date Tested", null=True)
    working = models.BooleanField(verbose_name="Working", default=None, null=True)
    po = models.ForeignKey(
        purchaseOrders, on_delete=models.PROTECT, verbose_name="PO", null=True
    )
    so = models.ForeignKey(
        salesOrders, on_delete=models.PROTECT, verbose_name="SO", null=True
    )
    warehouse = models.ForeignKey(
        warehouse, on_delete=models.PROTECT, verbose_name="Warehouse", null=True
    )

    history = HistoricalRecords()
    objects = deviceManager()
    all_objects = models.Manager()


class BackMarketListing(models.Model):
    listing_id = models.IntegerField(unique=True, primary_key=True)
    sku = models.ForeignKey(
        deviceAttributes, on_delete=models.PROTECT, verbose_name="SKU", null=True
    )
    bm_sku = models.CharField(max_length=20, verbose_name="BM SKU")
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    quantity = models.IntegerField(null=True, blank=True)
    backmarket_id = models.IntegerField()
    product_id = models.UUIDField()
    max_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    history = HistoricalRecords()


class faults(models.Model):
    id = models.AutoField(primary_key=True)
    device = models.ForeignKey(devices, on_delete=models.CASCADE)
    fault = models.CharField(max_length=20, verbose_name="Fault")
    repaired = models.BooleanField(verbose_name="Repaired", default=False)
    date_repaired = models.DateField(verbose_name="Date Repaired", null=True)
    repaired_by = models.CharField(max_length=20, verbose_name="Repaired By", null=True)
    repair_cost = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Repair Cost", null=True
    )

    def __str__(self):
        return self.fault
