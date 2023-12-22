# products/tables.py
import django_tables2 as tables
from .models import trackingDb


class TrackingTable(tables.Table):
    class Meta:
        model = trackingDb
