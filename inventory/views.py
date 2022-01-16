from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Company, Item, ItemInventory, Shipment
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.contrib import messages #TODO: add message handling to template
                                    #      & create messages to display in views
from django.urls import reverse
from .forms import ItemCreateForm, ShipmentCreateForm, ShipmentItemFormset

# Create your views here.
def landing_page(request):
    return render(request, 'inventory/home.html', {})

'''
TODO: convert this to a ListView
'''
def view_all_items(request):
    items = Item.objects.all()

    context = {
        'items': items,
        'itemCount': items.count()
    }

    return render(request, 'inventory/items-list.html', context=context)


'''
    The following class TODO
'''
class ItemCreateView(CreateView):
    template_name = 'inventory/items/item_create.html'
    form_class = ItemCreateForm
    model = Item

    def form_valid(self, form):
        print(form.fields)
        # View-specific form validation goes here
        starting_quantity = form.data['starting_inventory']
        # We want to proceed with saving the item
        response = super().form_valid(form)

        # Initialize this item's inventory to 0
        inventory = ItemInventory.objects.create(
            item=form.instance,
            quantity=starting_quantity
        )

        return response






'''
    The following class TODO
'''
class ItemDetailView(DetailView):
    template_name = 'inventory/items/item_detail.html'
    def get_object(self):
        item_id = self.kwargs.get("id")
        return get_object_or_404(Item, id=item_id)


'''
    The following class TODO
'''
class ItemUpdateView(UpdateView):
    template_name = 'inventory/items/item_update.html'
    form_class = ItemCreateForm
    model = Item

    def get_object(self):
        item_id = self.kwargs.get("id")
        return get_object_or_404(Item, id=item_id)


'''
    The following class TODO
'''
class ItemDeleteView(DeleteView):
    template_name = 'inventory/items/item_delete.html'

    def get_object(self):
        item_id = self.kwargs.get("id")
        return get_object_or_404(Item, id=item_id)


class ShipmentListView(ListView):
    model = Shipment
    template_name = 'inventory/shipments/shipment_list.html'

    def get_queryset(self):
        print(self.kwargs['company'])
        self.company = get_object_or_404(Company, id=self.kwargs['company'])
        return Shipment.objects.filter(company=self.company)

class ShipmentCreateView(CreateView):
    template_name = 'inventory/shipments/create_shipment.html'
    form_class = ShipmentCreateForm

    def get_success_url(self):
        return reverse('view-all-shipments', kwargs={'company': self.company.id})

    def form_valid(self, form):
        self.company = get_object_or_404(Company, id=self.kwargs['company'])
        shipment = form.save(commit=False)
        form.instance.company= self.company
        is_valid = super().form_valid(form)
        return is_valid

class ShipmentEditItemView(SingleObjectMixin, FormView):
    template_name = 'inventory/shipments/add_items_to_shipment.html'
    model = Shipment

    def get(self, request, *args, **kwargs):
        #TODO: get & pass inventory data so the maximum a shipment can take is
        # displayed on the form
        self.object = self.get_object(
            queryset=Shipment.objects.all()
        )
        return super.get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(
            queryset=Shipment.objects.all()
        )
        return super.post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        current_shipment = self.object
        return ShipmentItemFormset(**self.get_form_kwargs(), instance=current_shipment)

    def form_valid(self, form):
        form.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('view_all_items')
