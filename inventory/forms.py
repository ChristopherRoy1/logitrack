from django import forms
from .models import Item, Shipment, ShipmentItem, Company
from django.forms.models import inlineformset_factory

class ItemCreateForm(forms.ModelForm):
    starting_inventory = forms.IntegerField(initial=0)

    class Meta:
        model = Item
        fields = [
            'sku', 'company', 'product_name', 'is_shippable', 'weight_value',
            'weight_unit', 'dimension_x_value', 'dimension_y_value',
            'dimension_z_value', 'dimension_unit'
        ]


class ShipmentCreateForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = [
            'to_address', 'date_shipping', 'direction'
        ]


ShipmentItemFormset = inlineformset_factory(Shipment, ShipmentItem, fields=('item', 'quantity'), extra=10)
