from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models import Sum

import datetime

# Create your models here.

class Item(models.Model):
    '''
        The following class model represents the items held in the logistic
        company's warehouse.

        Because the logistics company serves many different clients, each with
        their own set of items, each instance of the Item model is associated
        to a Company.

    '''
    class DimensionUnit(models.TextChoices):
        M = 'm', 'Meters'
        FT = 'ft', 'Feet'

    class WeightUnit(models.TextChoices):
        KG = 'kg', 'Kilogram'
        LB = 'lb', 'Pound'
        OZ = 'oz', 'Ounces'


    # The identifier used to differentiate between different items. Included
    # on the printing labels in the warehouse to help with picking for shipments.
    # At the time of writing, SKUs must be unique across all companies. It is
    # planned to enforce uniqueness only across items within a company, and not
    # global uniqueness as currently implemented.
    sku = models.CharField(max_length=16, unique=True)


    company = models.ForeignKey (
        'Company',
        on_delete=models.PROTECT,
        related_name="item_company"
    )

    # The common name of the item
    product_name = models.CharField(max_length=200)

    # This field tracks the quantity available to be assigned to a shipment
    quantity_available = models.PositiveIntegerField(default=0)

    # The date_create and date_last_modified fields are currently for display
    # purposes, but will eventually be used for reporting & forecasting
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    # This field is used to control whether this item should ever be included
    # in an outbound shipment
    is_shippable = models.BooleanField(default=False)

    # Fields to keep track of weight, currently used for display purposes but
    # will eventually be used to help optimize the warehouse's shipments &
    # cost structure
    weight_value = models.FloatField()
    weight_unit = models.CharField(
        max_length=2,
        choices=WeightUnit.choices,
        default=WeightUnit.KG
    )

    # Fields to keep track of dimensions - important for shipment logic that
    # will be implemented in future builds of the software
    dimension_x_value = models.FloatField()
    dimension_y_value = models.FloatField()
    dimension_z_value = models.FloatField()

    dimension_unit = models.CharField(
        max_length=2,
        choices=DimensionUnit.choices,
        default=DimensionUnit.M
    )



    def can_calculate_volume(self):
        """ A helper method to determine whether an item's volume can be calculated """
        return not (self.dimension_x_value is None or self.dimension_y_value is None or self.dimension_x_value is None)

    def total_volume_unit(self):
        """ A helper method to return the units for an item's volume """
        if not self.can_calculate_volume():
            return None
        else:
            return "%(dimension_unit)s ^ 3" % self.dimension_unit

    def total_volume_value(self):
        """ A helper method to calculate an item's total volume """
        if not self.can_calculate_volume():
            return None
        else:
            return self.dimension_x_value * self.dimension_y_value * self.dimension_z_value

    def quantity_inbound(self):
        """
        A helper method to calculate the total quantity of the item on all
        inbound shipments. Used primarily to improve user experience across the
        different views & forms within Logitrack
        """
        query = ShipmentItem.objects.filter(
            item=self,
            shipment__is_shipped=False,
            shipment__direction='IN',
            is_open=True
        ).all().aggregate(Sum('quantity'))

        result = query['quantity__sum'] if query['quantity__sum'] is not None else 0
        return result

    def quantity_allocated(self):
        """
        A helper method to calculate the total quantity of the item on
        outbound shipments for the item. Used primarily to improve user
        experience across the different views & forms within Logitrack
        """

        # Allocated quantity is the sum of the quantities of all of the
        # Shipment items that have not been shipped yet
        query = ShipmentItem.objects.filter(
            item_id=self.id,
            shipment__is_shipped=False,
            shipment__direction='OUT',
            is_open=True
        ).all().aggregate(Sum('quantity'))

        # Check for None before returning the result
        result = query['quantity__sum'] if query['quantity__sum'] is not None else 0
        return result

    def can_have_shipping_disabled(self):
        return self.quantity_allocated() == 0 and self.quantity_inbound() == 0

    def is_on_shipments(self):
        return self.quantity_allocated() > 0 or self.quantity_inbound() > 0

    def in_valid_delete_state(self):
        if self.is_on_shipments():
            return False


        return True

    def get_absolute_url(self):
        """
        A helper method used by some class-based views and templates.
        Returns the path to the Detail View for this Item instance.
        """
        view_name = 'view-item'
        return reverse(view_name, args=[self.id])

    def get_absolute_edit_url(self):
        """
        A helper method used by some class-based views and templates.
        Returns the path to the edit view for this Item instance.
        """
        view_name = 'edit-item'
        return reverse(view_name, args=[self.id])

    def get_absolute_delete_url(self):
        """
        A helper method used by some class-based views and templates.
        Returns the path to the Delete View for this Item instance.
        """
        view_name = 'delete-item'
        return reverse(view_name, args=[self.id])

    def __str__(self):
        """
        Returns the string used for the string representation
        of Item instances
        """
        fields_to_display = (self.company.name, self.sku, self.product_name)
        return '|'.join(fields_to_display)

    def delete(self):
        qty_inbound = self.quantity_inbound()
        qty_allocated = self.quantity_allocated()
        if qty_inbound > 0 or qty_allocated > 0:
            raise ValidationError(
                "You cannot delete an item that is on a shipment. Qty inbound: %(qty_inbound)s, Qty allocated: %(qty_allocated)s",
                params={'qty_inbound': qty_inbound, 'qty_allocated': qty_allocated},
                code="item_on_shipment"
            )
        else:
            super(Item, self).delete()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Item, self).save(*args, **kwargs)

    def clean(self):
        super(Item, self).clean()

        if not self.can_have_shipping_disabled() and not self.is_shippable:
            raise ValidationError(
                "You cannot set an item to be non-shippable when it is on shipments",
                code="disable_item_when_on_shipment"
            )



class Company(models.Model):
    '''
    The following class model represents the clients/different companies that
    the warehouse running the Logitrack software serves.

    At the time of writing, the model does not hold much information but
    is planned to be further developed in a future build of the software.
    '''
    # The common name of the company
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        """ Returns the string representation of Company instances """
        return self.name




class Shipment(models.Model):
    '''
        The following model captures header-level information about shipments
        to and from Logitrack's warehouse.

        Shipments can contain one or many items, represented as ShipmentItems.

        All shipments are associated to a single company, and all associated
        items on the shipment will belong to that same company as well.
    '''
    class ShipmentDirection(models.TextChoices):
        IN = 'IN', "Inbound"
        OUT = 'OUT', "Outbound"

    company = models.ForeignKey('Company', on_delete=models.PROTECT)
    to_address = models.CharField(max_length=256)


    date_created = models.DateTimeField(auto_now_add=True)

    # The date on which the shipment is expected to arrive. To be used
    # for upcoming planned Logitrack functionality.
    date_promised = models.DateTimeField()

    # The is_shipped field flags Shipment instances as either received if they
    # are inbound shipments, and 'Shipped' if they are outbound. This field also
    # drives changes to the associated item model's inventory in the case of
    # inbound shipments.
    is_shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(null=True, blank=True)

    # This field tracks the type of shipment, inbound or outbound.
    direction = models.CharField(
        max_length=3,
        choices=ShipmentDirection.choices,
        default=ShipmentDirection.OUT
    )

    def get_status(self):
        """
        A helper method to display the shipment status based on the Shipment's
        direction and is_shipped fields. Used primarily in templates.
        """
        if self.direction == 'OUT' and self.is_shipped:
            return 'Shipped'
        elif self.direction == 'OUT' and not self.is_shipped:
            return 'Pending Shipping'
        elif self.direction == 'IN' and self.is_shipped:
            return 'Received'
        elif self.direction == 'IN' and not self.is_shipped:
            return 'Pending Receipt'
        else:
            return 'UNKNOWN'



    def has_open_shipment_lines(self):
        """
            A helper method to validate whether any related ShipmentItems have
            not been shipped. This method is planned for use in a build of
            Logitrack that supports partial line-item fulfillment.
        """
        return ShipmentItem.objects.filter(shipment=self, is_open=True).count() > 0

    def clean(self, *args, **kwargs):
        """
            This method overrides the Shipment class' parent's Model.clean()
            method in order to update some non mandatory fields that may not be
            present on some forms.
        """
        super(Shipment, self).clean(*args, **kwargs)
        # In the event that the shipment is flagged as shipped
        # and no date_shipped value is provided, default the date_shipped to be
        # the current time
        if self.is_shipped and self.date_shipped is None:
            self.date_shipped = datetime.now()

    def save(self, *args, **kwargs):
        """
            This method overrides the Shipment class' Model.save()
            method in order to update its related ShipmentItem instance in the
            event that the Shipment is shipped.

            The updates & saves made to the related ShipmentItem instances
            initiates any updates of inventory quantities for the items. See
            the ShipmentItem model for more details.
        """
        super(Shipment, self).save(*args, **kwargs)
        # Check to see if ShipmentItems haven't been closed yet before updating
        # and triggering an adjustment of inventory.
        if self.is_shipped and self.has_open_shipment_lines():
            shipment_items = ShipmentItem.objects.filter(shipment=self)
            for shipment_item in shipment_items:
                # Update the shipment line so that it no longer factors into
                # any calculations
                shipment_item.is_open = False
                shipment_item.save()



class ShipmentItem(models.Model):
    '''
        The following model captures detail-level information about shipments
        to and from Logitrack's warehouse, primarily information regarding
        the items on the shipment and their quantities.

        The from_db class method is overridden here in order to compare
        old and new quantity values, so that an item's inventory can be adjusted
        accordingly. This is critical in the event that a user updates a
        ShipmentItem's quantity from 5 to 10 - the delta must be calculated in
        order to determine whether there is sufficient available inventory to
        permit the update.

    '''

    shipment = models.ForeignKey('Shipment', on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='shipmentitem_item')
    quantity = models.PositiveIntegerField()
    is_open = models.BooleanField(default=True)


    def valid_item_for_company(self):
        return self.shipment.company.id == self.item.company.id

    def can_add_to_shipment(self):
        return self.shipment.direction == 'IN' or self.item.is_shippable

    @classmethod
    def from_db(cls, db, field_names, values):
        """
            This method overrides the ShipmentItem class' Model.from_db()
            method in order to cache the instance's values and calculate
            a delta between old and new quantity field values.
        """
        instance = super(ShipmentItem, cls).from_db(db, field_names, values)

        # It's important to keep track of how the quantity on a shipment item
        # has changed - shipment quantity is allocated at the time of create/update,
        # so if the quantity on a shipment item began at 50 but increased to 100,
        # the quantity available of the inventory should only increase by 100
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, *args, **kwargs):
        """
            This method overrides the ShipmentItem class' save()
            method in order to update the instance's associated Item's
            quantity_available on create or update.
        """
        # Force the model to clean before proceeding with the save (protects
        # against invalid model instances from being added by the Django shell)
        self.full_clean()

        shipment_direction = self.shipment.direction

        # The save method should behave differently if the ShipmentItem instance
        # is new to the database.
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
        """
            This method overrides the ShipmentItem class' clean()
            method in order to impose a set of validation constraints
            on ShipmentItems.
        """
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
                # This was explicitly left blank - there are no quantity
                # restrictions on inbound shipments

                pass


        super(ShipmentItem, self).clean(*args, **kwargs)



class SKUFormat(models.Model):
    '''
        The following model is planned to be used to impose restrictions
        on a company's SKU system for items.

        Development on this model and feature is being pushed to a future build.
    '''
    pass
