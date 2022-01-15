from django.contrib import admin
from inventory.models import Item, ItemInventory, Company
# Register your models here.
admin.site.register(Item)
admin.site.register(ItemInventory)
admin.site.register(Company)
