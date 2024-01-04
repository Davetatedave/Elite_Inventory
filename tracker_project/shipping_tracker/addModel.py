from .models import deviceAttributes

device={'sku':'IP13128GRAA',
'manufacturer':'Apple',
'model':'iPhone 13 Pro',
 'color':'Graphite',
'capacity':'128GB',
'carrier':None,
'grade':'A'}

deviceAttributes.objects.create(**device)