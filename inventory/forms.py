from django import forms
from .models import Item, Shipment, ShipmentItem, Company
from django.forms.models import inlineformset_factory, BaseInlineFormSet


class ItemCreateForm(forms.ModelForm):
    starting_inventory = forms.IntegerField(initial=0)

    class Meta:
        model = Item
        fields = [
            'sku', 'company', 'product_name', 'is_shippable', 'weight_value',
            'weight_unit', 'dimension_x_value', 'dimension_y_value',
            'dimension_z_value', 'dimension_unit'
        ]

class CompanyCreateForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = [
            'name'
        ]


class ShipmentCreateForm(forms.ModelForm):
    unique_fields = {'item'}

    class Meta:
        model = Shipment
        fields = [
            'to_address', 'date_promised', 'direction'
        ]


class ShipmentItemCreateFormSet(BaseInlineFormSet):

    class Meta:
        model = ShipmentItem
        fields= ['item', 'quantity']

    def __init__(self, *args, **kwargs):
        company_id = kwargs['instance'].company.id
        super(ShipmentItemCreateFormSet, self).__init__(*args, **kwargs)

        # Update each choice field to prevent selection of an item from a
        # different company.
        for form in self.forms:
            form.fields['item'].queryset = Item.objects.filter(company=company_id, is_shippable=True)






ShipmentItemFormset = inlineformset_factory(Shipment, ShipmentItem, formset=ShipmentItemCreateFormSet, fields=('item', 'quantity'))
