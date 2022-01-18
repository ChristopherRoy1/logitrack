from django.contrib import admin
from inventory.models import Item, Company, Shipment, ShipmentItem
# Register your models here.
admin.site.register(Item)
admin.site.register(Company)
admin.site.register(ShipmentItem)
admin.site.register(Shipment)
