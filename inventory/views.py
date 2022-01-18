from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Company, Item, ItemInventory, Shipment, ShipmentItem
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.contrib import messages #TODO: add message handling to template
                                    #      & create messages to display in views
from django.urls import reverse
from .forms import ItemCreateForm, ShipmentCreateForm, ShipmentItemFormset, CompanyCreateForm

# Create your views here.
def landing_page(request):
    return render(request, 'inventory/home.html', {})

'''
TODO: convert this to a ListView
'''
def view_all_items(request):
    """TODO: populate docstring """
    items = Item.objects.all()

    context = {
        'items': items,
        'itemCount': items.count()
    }

    return render(request, 'inventory/items-list.html', context=context)

'''
    Item Views

'''

class ItemCreateView(CreateView):
    """
        TODO: add docstring
    """
    template_name = 'inventory/items/item_create.html'
    form_class = ItemCreateForm
    model = Item

    def form_valid(self, form):
        print(form.fields)

        # starting_quantity is a field added to the form that is
        # not part of the Item Model -> we will use it to
        # initialize an associated ItemInventory model instead
        starting_quantity = form.data['starting_inventory']


        response = super().form_valid(form)

        # Initialize this item's inventory to 0
        inventory = ItemInventory.objects.create(
            item=form.instance,
            quantity=starting_quantity
        )

        return response



class ItemDetailView(DetailView):
    """
        The following class is used to display information about a single item.

        The item being requested is passed as a kwarg, which is used in the
        overriden get_object function to retrieve the associated item
        from the database.
    """

    template_name = 'inventory/items/item_detail.html'

    def get_object(self):
        item_id = self.kwargs.get("id")
        return get_object_or_404(Item, id=item_id)


class ItemUpdateView(UpdateView):
    """
        TODO: add docstring
    """
    template_name = 'inventory/items/item_update.html'
    form_class = ItemCreateForm
    model = Item

    def get_object(self):
        item_id = self.kwargs.get("id")
        return get_object_or_404(Item, id=item_id)

    def get_context_data(self, *args, **kwargs):
        context = super(ItemUpdateView, self).get_context_data(*args, **kwargs)

        # Display existing shipments to the user, to provide feedback
        # in the event that they try to change the 'is_shippable' property
        # to false when there are pending shipments
        item_id = self.kwargs.get("id")
        context['shipmentItems'] = ShipmentItem.objects.filter(item=item_id)
        return context

class ItemDeleteView(DeleteView):
    """
        TODO: add docstring
    """
    template_name = 'inventory/items/item_delete.html'

    def get_object(self):
        item_id = self.kwargs.get("id")
        return get_object_or_404(Item, id=item_id)

'''
    Company Views

'''


class CompanyCreateView(CreateView):
    model = Company
    template_name='inventory/companies/company_create.html'
    form_class=CompanyCreateForm

    def get_success_url(self):
        return reverse('view-all-companies')

class CompanyDetailView(DetailView):
    """
        The following class is used to display information about a single company.

    """

    template_name = 'inventory/companies/company_detail.html'

    def get_object(self):
        company_id = self.kwargs.get("company")
        return get_object_or_404(Company, id=company_id)

class CompanyListView(ListView):
    model = Company
    template_name='inventory/companies/company_list.html'


'''
    Shipment Views

'''

class ShipmentListView(ListView):
    """
        TODO: add docstring
    """
    model = Shipment
    template_name = 'inventory/shipments/shipment_list.html'

    def get_queryset(self):
        print(self.kwargs['company'])
        self.company = get_object_or_404(Company, id=self.kwargs['company'])
        return Shipment.objects.filter(company=self.company)

class ShipmentCreateView(CreateView):
    """
        TODO: add docstring
    """
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
    """
        TODO: add docstring
    """
    template_name = 'inventory/shipments/add_items_to_shipment.html'
    model = Shipment

    pk_url_kwarg='shipmentid'
    #def get_object(self):
    #    shipment_id = self.kwargs.get("shipmentid")
    #    return get_object_or_404(Shipment, id=shipment_id)


    def get(self, request, *args, **kwargs):
        #TODO: get & pass inventory data so the maximum a shipment can take is
        # displayed on the form'
        print(request)
        print(self.kwargs)
        self.object = self.get_object(queryset=Shipment.objects.all())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        #print('post detected')
        self.object = self.get_object(queryset=Shipment.objects.all())
        #print(self.get_form())
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        print('self.get_form_kwargs')
        print(self.get_form_kwargs())
        return ShipmentItemFormset(**self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        #print(form.instance)
        form.save()

        return super().form_valid(form)

    def get_success_url(self):
        print('getting_success_url')
        return '/'
