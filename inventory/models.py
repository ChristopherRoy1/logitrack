from django.db import models

# Create your models here.

'''
    The following class ... TODO
'''
class Item(models.Model):
    sku = models.CharField(max_length=16)
    company = models.ForeignKey('Company', on_delete=models.PROTECT)

    product_name = models.CharField(max_length=200)

    date_created = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    is_shippable = models.BooleanField(default=False)

    # Fields to keep track of weight
    weight_value = models.FloatField()
    weight_unit = models.CharField(
        max_length=2,
        choices=WeightUnit.choices,
        default=WeightUnit.KILO
    )

    # Fields to keep track of dimensions - important for shipment logic
    dimension_x_value = models.FloatField()
    dimension_y_value = models.FloatField()
    dimension_z_value = models.FloatField()

    dimension_unit = models.CharField(
        max_length=2,
    )


    class DimensionUnit(models.TextChoices):
        M = 'm', 'Meters'
        FT = 'ft', 'Feet'

    class WeightUnit(models.TextChoices):
        KG = 'kg', 'Kilogram'
        LB = 'lb', 'Pound'
        OZ = 'oz', 'Ounces'



'''
    The following class ... TODO
'''
class Company(models.Model):
    name = models.CharField(max_length=200)
    pass


'''
    The following class ... TODO
'''
class ItemInventory(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    quantity = models.IntegerField()




'''
    The following class ... TODO
'''
class Shipment(models.Model):
    pass

'''
    The following class ... TODO
'''
class ShipmentItem(models.Model):
    pass


'''
    The following class ... TODO
'''
class SKUFormat(models.Model):
    pass
