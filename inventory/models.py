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

    sku = models.CharField(max_length=16, unique=True)
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



    def can_calculate_volume(self):
        return not (self.dimension_x_value is None or self.dimension_y_value is None or self.dimension_x_value is None)

    def total_volume_unit(self):
        if not self.can_calculate_volume():
            return None
        else:
            return "%(dimension_unit)s ^ 3" % self.dimension_unit

    def total_volume_value(self):
        if not self.can_calculate_volume():
            return None
        else:
            return self.dimension_x_value * self.dimension_y_value * self.dimension_z_value

    def quantity_inbound(self):
        query = ShipmentItem.objects.filter(item=self, shipment__is_shipped=False, shipment__direction='IN').aggregate(Sum('quantity'))

        result = query['quantity__sum'] if query['quantity__sum'] is not None else 0
        return result

    def quantity_allocated(self):
        #TODO: search on all item shipments
        query = ShipmentItem.objects.filter(item=self, shipment__is_shipped=False, shipment__direction='OUT').aggregate(Sum('quantity'))
        result = query['quantity__sum'] if query['quantity__sum'] is not None else 0
        return result

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
    name = models.CharField(max_length=200, unique=True)

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
            self.date_shipped = datetime.now()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_shipped and self.has_open_shipment_lines():
            shipment_items = ShipmentItem.objects.filter(shipment=self)
            print(shipment_items)
            for shipment_item in shipment_items:
                # Update the shipment line so that it no longer factors into
                # the calculation
                shipment_item.is_open = False
                shipment_item.save()



class ShipmentItem(models.Model):
    """ShipmentItems represent line items on a Shipment """

    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='shipmentitem_item')
    quantity = models.PositiveIntegerField()
    is_open = models.BooleanField(default=True)


    def valid_item_for_company(self):
        return self.shipment.company.id == self.item.company.id

    def can_add_to_shipment(self):
        return self.shipment.direction == 'IN' or self.item.is_shippable

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(ShipmentItem, cls).from_db(db, field_names, values)

        # It's important to keep track of how the quantity on a shipment item
        # has changed - shipment quantity is allocated at the time of create/update,
        # so if the quantity on a shipment item began at 50 but increased to 100,
        # the quantity available of the inventory should only increase by 100
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, *args, **kwargs):
        # Force the model to clean before proceeding with the save (protects
        # against invalid model instances from being added by the Django shell)
        self.full_clean()

        shipment_direction = self.shipment.direction
        if self._state.adding:
            if shipment_direction == 'OUT':
                self.item.quantity_available -= self.quantity
            else:
                self.item.quantity_available += self.quantity

            self.item.save()

        elif self.quantity != self._loaded_values['quantity']:
            cur_qty = self.quantity
            old_qty = self._loaded_values['quantity']

            qty_difference = cur_qty - old_qty

            if shipment_direction == 'OUT':
                self.item.quantity_available -= qty_difference
            else:
                self.item.quantity_available += qty_difference

            self.item.save()

        super(ShipmentItem, self).save(*args, **kwargs)

    def delete(self):
        """ Override the delete method to adjust item inventory accordingly """

        shipment_direction = self.shipment.direction
        if shipment_direction == 'OUT':
            # Unallocate the Inventory
            self.item.quantity_available += self.quantity
        else:
            self.item.quantity_available -= self.quantity

        self.item.save()
        super(ShipmentItem, self).delete()


    def clean(self, *args, **kwargs):
        item_inventory_quantity = self.item.quantity_available
        shipment_direction = self.shipment.direction

        if item_inventory_quantity is None:
            raise ValidationError(
                "An unexpected error occured. The item was not added to the shipment",
                code="missing_inventory_record"
            )

        if not self.valid_item_for_company():
            raise ValidationError(
                "An unexpected error occured. All items on a shipment must belong to the company",
                code="incompatible_company"
            )

        if not self.can_add_to_shipment():
            raise ValidationError(
                "An unexpected error occured. The selected item is not eligible to be added to this shipment type",
                code="item_not_shippable"
            )

        if self._state.adding:

            if shipment_direction == "OUT" and self.quantity > item_inventory_quantity:
                raise ValidationError(
                    "An outbound shipment cannot ship more inventory than is available. Inventory Qty: %(qty_inv)s - Entered Qty: %(ship_qty)s",
                    params={'qty_inv': item_inventory_quantity, 'ship_qty': self.quantity},
                    code="invalid_inventory_quantity"
                )
        elif self.quantity != self._loaded_values['quantity']:
            # We need to make sure that an increase in quantity does not
            # exceed the available inventory

            cur_qty = self.quantity
            old_qty = self._loaded_values['quantity']
            avail_qty = item_inventory_quantity

            qty_difference = cur_qty - old_qty


            if shipment_direction == 'OUT' and cur_qty > avail_qty + old_qty:
                raise ValidationError(
                    "Modifying this line would create negative inventory. Inventory Qty: %(qty_inv)s - Old Qty: %(old_qty)s - New Qty: %(new_qty)s",
                    params={'qty_inv': avail_qty, 'old_qty': old_qty, 'new_qty': cur_qty},
                    code="invalid_inventory_quantity_edit"
                )
            elif shipment_direction == 'IN':
                # This was explicitly left blank - no problems with updating inbound_shipment
                pass


        super(ShipmentItem, self).clean(*args, **kwargs)

        #    print(self.quantity)
        #    print(item_inventory_quantity)
        #








'''
    The following class ... TODO
'''
class SKUFormat(models.Model):
    pass
