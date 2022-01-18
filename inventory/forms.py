from django import forms
from .models import Item, Shipment, ShipmentItem, Company
from django.forms.models import inlineformset_factory, BaseInlineFormSet


class ItemCreateForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = [
            'sku', 'company', 'product_name', 'is_shippable', 'weight_value',
            'weight_unit', 'dimension_x_value', 'dimension_y_value',
            'dimension_z_value', 'dimension_unit', 'quantity_available'
        ]

class CompanyCreateForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = [
            'name'
        ]



class ShipmentShipForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = [
            'is_shipped', 'date_shipped'
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

    def save(self, commit=True, *args, **kwargs):
        print('save item create formset')
        print(dir(self))
        super(ShipmentItemCreateFormSet, self).save(*args, **kwargs)






ShipmentItemFormset = inlineformset_factory(Shipment, ShipmentItem, formset=ShipmentItemCreateFormSet, fields=('item', 'quantity'))
