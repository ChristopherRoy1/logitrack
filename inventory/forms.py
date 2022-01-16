from django import forms
from .models import Item


class ItemCreateForm(forms.ModelForm):
    sku = forms.CharField()

    class Meta:
        model = Item
        fields = [
            'sku', 'company', 'product_name', 'is_shippable', 'weight_value',
            'weight_unit', 'dimension_x_value', 'dimension_y_value',
            'dimension_z_value', 'dimension_unit'
        ]
