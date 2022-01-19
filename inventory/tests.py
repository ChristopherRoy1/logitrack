from django.test import TestCase
from inventory.models import Company, Item, Shipment, ShipmentItem
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from django.utils import timezone

# Create your tests here.
class CompanyTestCase(TestCase):
    def setUp(self):
        Company.objects.create(name="The Test Company")


    def test_name_field_unique(self):
        """Company name should be unique"""
        with self.assertRaises(IntegrityError):
            Company.objects.create(name="The Test Company")


class ItemTestCase(TestCase):
    def setUp(self):
        self.company1 = Company.objects.create(name="The Test Company")
        Item.objects.create(
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


    def test_unique_item_sku_same_company(self):
        with self.assertRaises(IntegrityError):
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
        company_w_same_sku = Company.objects.create(name="Company With Same Sku")
        with self.assertRaises(IntegrityError):
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
        with self.assertRaises(ValidationError):
            ship_item = ShipmentItem.objects.create(
                shipment = self.shipment1,
                item=self.item2,
                quantity=10
            )
            

    def test_non_shippable_item_add_outbound(self):
        self.item1.is_shippable = False
        self.item1.save()

        with self.assertRaises(ValidationError):
            ship_item = ShipmentItem(
                shipment = self.shipment1,
                item=self.item1,
                quantity=10
            ).full_clean()



    def test_non_shippable_item_shipment_type(self):
        # This shipment item's shipment is an outbound shipment,
        # which should raise an error as the item is flagged as non-shippable
        with self.assertRaises(ValidationError):
            ship_item = ShipmentItem.objects.create(
                shipment = self.shipment1,
                item=self.item1,
                quantity=10
            )

        # Now, switching the shipment direction to 'IN' (inbound) should not raise any validation errors
        self.shipment1.direction = 'IN'
        self.shipment1.save()

        ship_item = ShipmentItem.objects.create(
            shipment = self.shipment1,
            item=self.item1,
            quantity=10
        )
