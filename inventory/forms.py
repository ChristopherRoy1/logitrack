from django import forms
from .models import Item, Shipment, ShipmentItem, Company
from django.forms.models import inlineformset_factory, BaseInlineFormSet

"""
    The following classes override the default Django ModelForms
    behavior for the different classes within Logitrack.

    The ShipmentItemCreateFormSet is the only class within this file,
    at the time of writing, that overrides any default methods.

"""
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
        labels = {
            'date_shipped': 'Ship/Receive Date'
        }
        fields = [
            'date_shipped'
        ]




class ShipmentCreateForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = [
            'to_address', 'date_promised', 'direction'
        ]


class ShipmentItemCreateFormSet(BaseInlineFormSet):
    """
        The following formset is used to allow users to add multiple
        ShipmentItems to a Shipment at a time.

    """
    class Meta:
        model = ShipmentItem
        fields= ['item', 'quantity']

    def __init__(self, *args, **kwargs):
        """
            This method overrides the __init__ method in order to
            restrict the Select field options to items that are both
            shippable, and belonging to this company.
            The company is passed as a keyword argument to the
            view leveraging this formset.
        """
        company_id = kwargs['instance'].company.id
        # TODO: check direction of shipment to ensure shippable items
        # are only excluded from outbound shipments.
        super(ShipmentItemCreateFormSet, self).__init__(*args, **kwargs)

        # Update each choice field to prevent selection of an item from a
        # different company.
        for form in self.forms:
            form.fields['item'].queryset = Item.objects.filter(company=company_id, is_shippable=True)

    def save(self, commit=True, *args, **kwargs):
        super(ShipmentItemCreateFormSet, self).save(*args, **kwargs)






ShipmentItemFormset = inlineformset_factory(Shipment, ShipmentItem, formset=ShipmentItemCreateFormSet, fields=('item', 'quantity'))
