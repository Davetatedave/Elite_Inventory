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
