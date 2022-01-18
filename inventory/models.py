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

    quantity_available = models.PositiveIntegerField(default=0)


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

    def quantity_inbound(self):
        #TODO: search on all item shipments
        return 0

    def quantity_allocated(self):
        #TODO: search on all item shipments
        return 0

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
    date_shipped = models.DateTimeField(null=True, blank=True)

    direction = models.CharField(
        max_length=3,
        choices=ShipmentDirection.choices,
        default=ShipmentDirection.OUT
    )

    def get_status(self):
        if self.direction == 'OUT' and self.is_shipped:
            return 'Shipped'
        elif self.direction == 'OUT' and not self.is_shipped:
            return 'Pending'
        elif self.direction == 'IN' and self.is_shipped:
            return 'Received'
        elif self.direction == 'IN' and not self.is_shipped:
            return 'Pending Receipt'
        else:
            return 'UNKNOWN'



    def has_open_shipment_lines(self):
        return ShipmentItem.objects.filter(shipment=self, is_open=True).count() > 0

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        # In the event that the shipment is flagged as shipped
        # and no date_shipped value is provided, default the date_shipped to be
        # the current time
        if self.is_shipped and self.date_shipped is None:
            self.date_shipped = datetime.now

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_shipped and self.has_open_shipment_lines():
            shipment_items = ShipmentItem.objects.filter(shipment=self)
            for shipment_item in shipment_items:
                related_item = shipment_item.item

                # Update the item's quantity according to the shipment direction
                if self.direction == 'OUT':
                    related_item.quantity_available -= shipment_item.quantity
                else:
                    related_item.quantity_available += shipment_item.quantity

                related_item.save()
                # We also need to update the shipment lines
                shipment_item.is_open = False
                shipment_item.save()



class ShipmentItem(models.Model):
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='shipmentitem_item')
    quantity = models.PositiveIntegerField()
    is_open = models.BooleanField(default=True)

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)

        if self.quantity is not None and self.quantity < 0:
            raise ValidationError(
                'A shipment quantity must be non-negative',
                code='negative_qty'
            )

        item_inventory_quantity = self.item.quantity_available
        shipment_direction = self.shipment.direction

        if item_inventory_quantity is None:
            raise ValidationError(
                "An unexpected error occured. The item was not added to the shipment",
                code="missing_inventory_record"
            )

            print(self.quantity)
            print(item_inventory_quantity)
        if shipment_direction == "OUT" and self.quantity > item_inventory_quantity:
            raise ValidationError(
                "An outbound shipment cannot ship more inventory than is available. Inventory Qty: %(qty_inv)s - Entered Qty: %(ship_qty)s",
                params={'qty_inv': item_inventory_quantity, 'ship_qty': self.quantity},
                code="invalid_inventory_quantity"
            )








'''
    The following class ... TODO
'''
class SKUFormat(models.Model):
    pass
