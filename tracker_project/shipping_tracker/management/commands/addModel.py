from django.core.management.base import BaseCommand
from shipping_tracker.models import deviceAttributes

class Command(BaseCommand):
    def handle(self, **options):
        device={'sku':'IP13128GRAA',
        'manufacturer':'Apple',
        'model':'iPhone 13 Pro',
        'color':'Graphite',
        'capacity':'128GB',
        'carrier':'AT&T',
        'grade':'A'}

        deviceAttributes.objects.create(**device)