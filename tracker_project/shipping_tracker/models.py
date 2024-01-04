from django.db import models
from .utils import check_shipping_status


# Create your models here.
class trackingDb(models.Model):
    order_id = models.IntegerField(primary_key=True,verbose_name = "Order ID")
    ol_state = models.IntegerField(verbose_name = "State")
    shipper = models.CharField(max_length=20,verbose_name = "Shipper")
    tracking_number = models.CharField(max_length=20,verbose_name = "Tracking Number")
    date_creation = models.DateTimeField(null=True,verbose_name = "Creation Date")
    date_shipping = models.DateField(null=True,verbose_name = "Shipping Date")
    Shipping_Status = models.CharField(max_length=20,verbose_name = "Shipping Status")
    Expected_Arrival = models.DateField(null=True,verbose_name = "Expected Arrival")
    Arrival_Status = models.CharField(max_length=20,verbose_name = "Arrival Status")
    history = models.JSONField(verbose_name = "History")

    def status(self):
        return check_shipping_status(self)

class deviceAttributes(models.Model):
    sku = models.CharField(max_length=20,primary_key=True,verbose_name = "SKU")
    manufacturer = models.CharField(max_length=20,verbose_name = "Manufacturer")
    model = models.CharField(max_length=20,verbose_name = "Model")
    color = models.CharField(max_length=20,verbose_name = "Color")
    capacity = models.CharField(max_length=20,verbose_name = "Capacity")
    carrier = models.CharField(max_length=20,verbose_name = "Carrier",blank=True)
    grade=models.CharField(max_length=20,verbose_name = "Grade")
    
class devices(models.Model):
    imei = models.IntegerField(unique=True,verbose_name = "IMEI")
    sku = models.ForeignKey(deviceAttributes, on_delete=models.PROTECT,verbose_name = "SKU")
    status=models.CharField(max_length=20,verbose_name = "Status")
    