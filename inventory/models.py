from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models import Sum

import datetime

# Create your models here.

'''
    The following class ... TODO
'''
class Item(models.Model):

    class DimensionUnit(models.TextChoices):
        M = 'm', 'Meters'
        FT = 'ft', 'Feet'

    class WeightUnit(models.TextChoices):
        KG = 'kg', 'Kilogram'
        LB = 'lb', 'Pound'
        OZ = 'oz', 'Ounces'

    sku = models.CharField(max_length=16)
    company = models.ForeignKey('Company', on_delete=models.PROTECT, related_name="item_company")

    product_name = models.CharField(max_length=200)

    date_created = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    is_shippable = models.BooleanField(default=False)

    # Fields to keep track of weight
    weight_value = models.FloatField()
    weight_unit = models.CharField(
        max_length=2,
        choices=WeightUnit.choices,
        default=WeightUnit.KG
    )

    # Fields to keep track of dimensions - important for shipment logic
    dimension_x_value = models.FloatField()
    dimension_y_value = models.FloatField()
    dimension_z_value = models.FloatField()

    dimension_unit = models.CharField(
        max_length=2,
        choices=DimensionUnit.choices,
        default=DimensionUnit.M
    )

    def get_absolute_url(self):
        view_name = 'view-item'
        return reverse(view_name, args=[self.id])

    def get_absolute_edit_url(self):
        view_name = 'edit-item'
        return reverse(view_name, args=[self.id])

    def get_absolute_delete_url(self):
        view_name = 'delete-item'
        return reverse(view_name, args=[self.id])

    def __str__(self):
        fields_to_display = (self.company.name, self.sku, self.product_name)
        return '|'.join(fields_to_display)


'''
    The following class ... TODO
'''
class Company(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name



class ItemInventory(models.Model):
    '''
        The following model represents the inventory level of a related item.
        While the application does not support multiple locations, the
        inventory functionality was seperated from the Item model to simplify
        future development in the event that support for locations is added
    '''

    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name="item_iteminventory")
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.item.product_name + ': ' + str(self.quantity)

'''
    The following class ... TODO
'''
class Shipment(models.Model):
    class ShipmentDirection(models.TextChoices):
        IN = 'IN', "Inbound"
        OUT = 'OUT', "Outbound"

    company = models.ForeignKey('Company', on_delete=models.PROTECT)
    to_address = models.CharField(max_length=256)

    date_created = models.DateTimeField(auto_now_add=True)
    date_promised = models.DateTimeField()

    is_shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(null=True)

    direction = models.CharField(
        max_length=3,
        choices=ShipmentDirection.choices,
        default=ShipmentDirection.OUT
    )

    def clean(self, *args, **kwargs):
        super().clean()
        # In the event that the shipment is flagged as shipped
        # and no date_shipped value is provided, default the date_shipped to be
        # the current time
        if self.is_shipped and date_shipped is None:
            date_shipped = datetime.now



class ShipmentItem(models.Model):
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='shipmentitem_item')
    quantity = models.PositiveIntegerField()

    def clean(self):
        if self.quantity < 0:
            raise ValidationError(
                'A shipment quantity must be non-negative',
                code='negative_qty'
            )

        item_inventory_quantity = ItemInventory.objects.filter(item=self.item).aggregate(Sum('quantity'))['quantity__sum']

        if item_inventory_quantity is None:
            raise ValidationError(
                "An unexpected error occured. The item was not added to the shipment",
                code="missing_inventory_record"
            )

        if self.quantity > item_inventory_quantity:
            raise ValidationError(
                "A shipment item cannot be greater than an item's inventory. Inventory Qty: %(qty_inv)s - Entered Qty: %(ship_qty)s",
                params={'qty_inv': item_inventory_quantity, 'ship_qty': self.quantity},
                code="invalid_inventory_quantity"
            )




'''
    The following class ... TODO
'''
class SKUFormat(models.Model):
    pass
