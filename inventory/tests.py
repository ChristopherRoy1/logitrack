from django.test import TestCase
from inventory.models import Company, Item, Shipment, ShipmentItem
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from django.utils import timezone

class ItemTestCase(TestCase):
    def setUp(self):
        self.company1 = Company.objects.create(name="The Test Company")
        self.item1 = Item.objects.create(
            sku="BLU-SHRT-LG",
            company=self.company1,
            product_name="Blue Shirt (Large)",
            quantity_available=0,
            weight_value=10,
            weight_unit='kg',
            dimension_x_value=1,
            dimension_y_value=2,
            dimension_z_value=3
        )

        self.item2 = Item.objects.create(
            sku="BLU-SHRT-SM",
            company=self.company1,
            product_name="Blue Shirt (Small)",
            quantity_available=100,
            weight_value=10,
            weight_unit='kg',
            is_shippable=True,
            dimension_x_value=1,
            dimension_y_value=2,
            dimension_z_value=3
        )


    def test_unique_item_sku_same_company(self):
        """
            This test ensures that items cannot share SKUs within the same
            company. We attempt to create an item with the sku "BLU-SHRT-LG",
            which already exists in the db as a result of the setUp method.
        """
        with self.assertRaises(ValidationError):
            Item.objects.create(
                sku="BLU-SHRT-LG",
                company=self.company1,
                product_name="Blue Shirt (Large) Duplicate",
                quantity_available=100,
                weight_value=10,
                weight_unit='kg',
                dimension_x_value=1,
                dimension_y_value=2,
                dimension_z_value=3
            )

    def test_unique_item_sku_diff_company(self):
        """
            This test ensures that duplicate item SKUs cannot exist across
            companies. The plan is to eventually remove this test as
            sku uniqueness will be supported only within a company, and
            not globally.
        """
        company_w_same_sku = Company.objects.create(name="Company With Same Sku")
        with self.assertRaises(ValidationError):
            Item.objects.create(
                sku="BLU-SHRT-LG",
                company=company_w_same_sku,
                product_name="Blue Shirt (Large) Duplicate",
                quantity_available=100,
                weight_value=10,
                weight_unit='kg',
                dimension_x_value=1,
                dimension_y_value=2,
                dimension_z_value=3
            )

    def test_delete_item_with_open_shipments(self):
        """
            This test is to ensure that Logitrack does not allow
            the deletion of items that are on shipments.
        """
        shipment = Shipment.objects.create(
            company = self.company1,
            to_address = "Test address 1234",
            date_promised=timezone.now(),
            is_shipped=False,
            direction='OUT'
        )

        ShipmentItem.objects.create(
            item=self.item2,
            quantity=10,
            shipment=shipment
        )


        with self.assertRaises(ValidationError):
            # Updating the is_shippable field to false when there is already
            # an open shipment with this item on it should fail.
            self.item2.is_shippable=False
            self.item2.save()

    def test_update_shippable_item_with_closed_shipments(self):
        """
            This test is to ensure that Logitrack allows for items to be
            deleted when all shipments that they were on are closed.
        """
        shipment = Shipment.objects.create(
            company = self.company1,
            to_address = "Test address 1234",
            date_promised=timezone.now(),
            is_shipped=False,
            direction='OUT'
        )

        ShipmentItem.objects.create(
            item=self.item2,
            quantity=10,
            shipment=shipment
        )

        with self.assertRaises(ValidationError):
            # Updating the is_shippable field to false when there is already
            # an open shipment with this item on it should fail.
            self.item2.is_shippable=False
            self.item2.save()

        # Once we update the shipment to true, now the item should be eligible
        # to be modified.
        shipment.is_shipped=True
        shipment.save()

        self.item2.is_shippable=False
        self.item2.save()


    def test_delete_item_that_has_been_shipped(self):
        """
            This test is to ensure that items can be deleted once
            all inbound and outbound shipments associated with it have
            been shipped/received.
        """
        shipment = Shipment.objects.create(
            company = self.company1,
            to_address = "Test address 1234",
            date_promised=timezone.now(),
            is_shipped=False,
            direction='OUT'
        )

        shipment2 = Shipment.objects.create(
            company = self.company1,
            to_address = "Test address 1234",
            date_promised=timezone.now(),
            is_shipped=False,
            direction='IN'
        )

        ShipmentItem.objects.create(
            item=self.item2,
            quantity=10,
            shipment=shipment
        )

        ShipmentItem.objects.create(
            item=self.item2,
            quantity=10,
            shipment=shipment2
        )

        shipment.is_shipped=True
        shipment.save()

        # The attempt to delete should fail, as shipment2, which has the
        # item associated to it, is still not received
        with self.assertRaises(ValidationError):
            self.item2.delete()

        shipment2.is_shipped=True
        shipment2.save()

        # This should no longer raise any exceptions
        self.item2.delete()


class ItemClassMethodTestCase(TestCase):
    def setUp(self):
        self.company1 = Company.objects.create(name="The Test Company")
        self.item1 = Item.objects.create(
            sku="BLU-SHRT-LG",
            company=self.company1,
            product_name="Blue Shirt (Large) Duplicate",
            quantity_available=100,
            weight_value=10,
            weight_unit='kg',
            dimension_x_value=1,
            dimension_y_value=2,
            dimension_z_value=3
        )

    def test_method_can_have_shipping_disabled(self):
        """
            This is a test to validate the can_have_shipping_disabled Item
            model method
        """
        # The item is not on any shipments, so it should be able to be disabled
        self.assertTrue(self.item1.can_have_shipping_disabled())

        shipment = Shipment.objects.create(
            company = self.company1,
            to_address = "Test address 1234",
            date_promised=timezone.now(),
            is_shipped=False,
            direction='OUT'
        )

        self.item1.is_shippable = True

        shipment_item = ShipmentItem.objects.create(
            shipment = shipment,
            item=self.item1,
            quantity=10
        )


        self.assertFalse(self.item1.can_have_shipping_disabled())

    def test_method_is_on_shipments(self):
        """
            The following test validates the behavior of the
            Item model's is_on_shipments method
        """
        self.assertFalse(self.item1.is_on_shipments())

        shipment = Shipment.objects.create(
            company = self.company1,
            to_address = "Test address 1234",
            date_promised=timezone.now(),
            is_shipped=False,
            direction='OUT'
        )

        self.item1.is_shippable = True

        shipment_item = ShipmentItem.objects.create(
            shipment = shipment,
            item=self.item1,
            quantity=10
        )


        self.assertTrue(self.item1.is_on_shipments())

    def test_method_in_valid_delete_state(self):
        """
            The following test validates the in_valid_delete_state method
            behavior of the Item model.
        """
        self.assertFalse(self.item1.is_on_shipments())
        self.assertTrue(self.item1.in_valid_delete_state())

        shipment = Shipment.objects.create(
            company = self.company1,
            to_address = "Test address 1234",
            date_promised=timezone.now(),
            is_shipped=False,
            direction='OUT'
        )

        self.item1.is_shippable = True

        shipment_item = ShipmentItem.objects.create(
            shipment = shipment,
            item=self.item1,
            quantity=10
        )

        self.assertTrue(self.item1.is_on_shipments())
        self.assertFalse(self.item1.in_valid_delete_state())




class ItemClassQuantityMethodTestCase(TestCase):
    def setUp(self):
        self.company1 = Company.objects.create(name="The Test Company")
        self.item1 = Item.objects.create(
            sku="BLU-SHRT-LG",
            company=self.company1,
            product_name="Blue Shirt (Large) Duplicate",
            quantity_available=100,
            is_shippable=True,
            weight_value=10,
            weight_unit='kg',
            dimension_x_value=1,
            dimension_y_value=2,
            dimension_z_value=3
        )
        self.shipment1 = Shipment.objects.create(
            company = self.company1,
            to_address = "Test address 1234",
            date_promised=timezone.now(),
            is_shipped=False,
            direction='OUT'
        )


    def test_method_quantity_allocated(self):
        """
            The following test validates the quantity_allocated method behavior
            of the Item model.
        """
        self.assertEquals(self.item1.quantity_allocated(), 0)
        shipment_item = ShipmentItem.objects.create(
            item=self.item1,
            shipment=self.shipment1,
            quantity=2
        )
        self.assertEquals(self.item1.quantity_allocated(), 2)
        self.shipment1.is_shipped=True
        self.shipment1.save()

        self.assertEquals(self.item1.quantity_allocated(), 0)


class ShipmentItemTestCase(TestCase):
    def setUp(self):
        self.company1 = Company.objects.create(name="The Test Company")
        self.company2 = Company.objects.create(name="Another Company")

        self.item1 = Item.objects.create(
            sku="BLU-SHRT-LG",
            company=self.company1,
            product_name="Blue Shirt (Large) Duplicate",
            quantity_available=100,
            weight_value=10,
            weight_unit='kg',
            dimension_x_value=1,
            dimension_y_value=2,
            dimension_z_value=3
        )

        self.item2 = Item.objects.create(
            sku="RED-PNT-SM",
            company=self.company2,
            product_name="Red Pant (Small)",
            quantity_available=100,
            weight_value=10,
            weight_unit='kg',
            dimension_x_value=1,
            dimension_y_value=2,
            dimension_z_value=3
        )

        self.shipment1 = Shipment.objects.create(
            company = self.company1,
            to_address = "Test address 1234",
            date_promised=timezone.now(),
            is_shipped=False,
            direction='OUT'
        )


    def test_shipment_item_company_mismatch(self):
        """
            This is a test to make sure that a company's shipments can only
            contain items that are associated to them
        """
        with self.assertRaises(ValidationError):
            ship_item = ShipmentItem.objects.create(
                shipment = self.shipment1,
                item=self.item2,
                quantity=10
            )


    def test_non_shippable_item_add_outbound(self):
        """
            This is a test to make sure that an item flagged as 'non_shippable'
            cannot be added to an outbound shipment
        """
        self.item1.is_shippable = False
        self.item1.save()

        with self.assertRaises(ValidationError):
            ship_item = ShipmentItem.objects.create(
                shipment = self.shipment1,
                item=self.item1,
                quantity=10
            )



    def test_non_shippable_item_shipment_type(self):
        """
            This is a test to make sure that any item for a company can be added
            to a shipment, regardless of whether they are flagged as 'is_shippable'
        """
        # Now, switching the shipment direction to 'IN' (inbound) should not raise any validation errors
        self.shipment1.direction = 'IN'
        self.shipment1.save()

        ship_item = ShipmentItem.objects.create(
            shipment = self.shipment1,
            item=self.item1,
            quantity=10
        )


    def test_shippable_item_quantity(self):
        """
            This is a test to make sure that an outbound shipment cannot be
            assigned an quantity of an item that's greater than what is currently
            available in inventory
        """

        self.item1.is_shippable = True
        self.item1.quantity_available = 599

        with self.assertRaises(ValidationError):
            ship_item = ShipmentItem.objects.create(
                shipment = self.shipment1,
                item=self.item1,
                quantity=600
            )

class OutboundShipmentQuantityTestCase(TestCase):
    def setUp(self):
        self.company1 = Company.objects.create(name="The Test Company")

        self.shippableItem1 = Item.objects.create(
            sku="BLU-SHRT-LG",
            company=self.company1,
            product_name="Blue Shirt (Large) Duplicate",
            quantity_available=10,
            weight_value=10,
            weight_unit='kg',
            is_shippable=True,
            dimension_x_value=1,
            dimension_y_value=2,
            dimension_z_value=3
        )

        self.shipment1 = Shipment.objects.create(
            company = self.company1,
            to_address = "Test address 1234",
            date_promised=timezone.now(),
            is_shipped=False,
            direction='OUT'
        )

        self.shipment2 = Shipment.objects.create(
            company = self.company1,
            to_address = "Test address 1234",
            date_promised=timezone.now(),
            is_shipped=False,
            direction='IN'
        )

    def test_update_ship_item_quantity_allocated(self):
        """
            This is a test to validate that item inventory is properly allocated
            when updating a shipment item on an outbound shipment.

            The item in question has 10 units available in inventory.
            We will create and then update a ShipmentItem, and validate the
            associated Item models' available quantity.
        """

        shipment_item = ShipmentItem.objects.create(
            shipment=self.shipment1,
            item = self.shippableItem1,
            quantity= 5
        )

        self.assertEquals(self.shippableItem1.quantity_allocated(), 5)
        self.assertEquals(self.shippableItem1.quantity_available, 5)

        shipment_item = ShipmentItem.objects.get(pk=shipment_item.pk)
        shipment_item.quantity = 10
        shipment_item.save()

        # The item object is updated on save of shipment_item, so
        # query the database again for the item to validate inventory level
        self.shippableItem1 = Item.objects.get(pk=self.shippableItem1.pk)

        self.assertEquals(self.shippableItem1.quantity_allocated(), 10)
        self.assertEquals(self.shippableItem1.quantity_available, 0)


    def test_delete_ship_item_inventory_allocated(self):
        """
            This is a test to ensure that Shipment Items that get deleted
            have the corresponding Item instance's quantity_available replenished
            by the deleted amount.
        """

        shipment_item = ShipmentItem.objects.create(
            shipment=self.shipment1,
            item = self.shippableItem1,
            quantity= 5
        )

        self.assertEquals(self.shippableItem1.quantity_allocated(), 5)
        self.assertEquals(self.shippableItem1.quantity_available, 5)

        shipment_item.delete()

        # Reload the
        self.shippableItem1 = Item.objects.get(pk=self.shippableItem1.pk)
        self.assertEquals(self.shippableItem1.quantity_allocated(), 0)
        self.assertEquals(self.shippableItem1.quantity_available, 10)


    def test_delete_item_with_open_shipments(self):
        pass


# Create your tests here.
class CompanyTestCase(TestCase):
    def setUp(self):
        Company.objects.create(name="The Test Company")


    def test_name_field_unique(self):
        """ This test validates that a Company's name field must be unique"""
        with self.assertRaises(IntegrityError):
            Company.objects.create(name="The Test Company")
