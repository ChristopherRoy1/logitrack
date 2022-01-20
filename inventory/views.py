from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from .models import Company, Item, Shipment, ShipmentItem
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.contrib import messages
from django.urls import reverse
from .forms import ItemCreateForm, ShipmentCreateForm, ShipmentShipForm, ShipmentItemFormset, CompanyCreateForm

from django.utils import timezone


"""
    Function based views
"""

# Create your views here.
def landing_page(request):
    """
        The following function handles requests for the
        homepage of the application.
    """
    return render(request, 'inventory/home.html', {})


def view_all_items(request):
    """
        The following function handles requests to view all items
        currently present in Logitrack.
    """

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
        The following class implements the CREATE view for items within
        Logitrack. It is a subclass of the generic CreateView supplied by
        Django.
    """
    template_name = 'inventory/items/item_create.html'
    form_class = ItemCreateForm
    model = Item



class ItemDetailView(DetailView):
    """
        The following class implements the READ/DETAIL view for a single item.
        It is a subclass of the generic DetailView supplied by Django.

        The item being requested is passed as a kwarg, which is used in the
        overriden get_object function to retrieve the associated item
        from the database.
    """

    template_name = 'inventory/items/item_detail.html'

    def get_object(self):
        """
            This method retrieves the ID of the requested item from the URL
            and returns the corresponding item, if it exists in the database.
            If the item does not exist, a 404 response is returned.
        """
        item_id = self.kwargs.get("id")
        return get_object_or_404(Item, id=item_id)


class ItemUpdateView(UpdateView):
    """
        The following class implements the EDIT view for the items within
        Logitrack. It is a subclass of the generic UpdateView supplied by Django.
    """
    template_name = 'inventory/items/item_update.html'
    form_class = ItemCreateForm
    model = Item

    def get_object(self):
        """
            This method retrieves the ID of the requested item from the URL
            and returns the corresponding item, if it exists in the database.
            If the item does not exist, a 404 response is returned.
        """
        item_id = self.kwargs.get("id")
        return get_object_or_404(Item, id=item_id)

    def get_context_data(self, *args, **kwargs):
        """
            The following method overrides the UpdateView's get_context_data()
            method, in order to include shipment information when updating an item.
        """
        context = super(ItemUpdateView, self).get_context_data(*args, **kwargs)

        item_id = self.kwargs.get("id")
        item_company = Item.objects.filter(id=item_id).values('company').distinct()

        context['shipments'] = Shipment.objects.filter(company__in=item_company)

        return context


class ItemDeleteView(DeleteView):
    """
        The following class implements the DELETE view for items within
        Logitrack.
    """
    template_name = 'inventory/items/item_delete.html'
    model = Item


    def get_object(self):
        """
            This method retrieves the ID of the requested item from the URL
            and returns the corresponding item, if it exists in the database.
            If the item does not exist, a 404 response is returned.
        """
        item_id = self.kwargs.get("id")
        return get_object_or_404(Item, id=item_id)

    def form_valid(self, request, *args, **kwargs):
        """
            This method helps prevent server errors if a user navigates directly
            to an item URL to delete the item, and raises a 403 code instead.
        """
        item = self.get_object()
        if item.in_valid_delete_state():
            return super(ItemDeleteView, self).form_valid(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You cannot delete this item. Validate whether it is on shipments, and try again")


'''
    Company Views

'''

class CompanyCreateView(CreateView):
    """
        The following class is used to allow users to create companies
        within Logitrack.
    """
    model = Company
    template_name='inventory/companies/company_create.html'
    form_class=CompanyCreateForm

    def get_success_url(self):
        return reverse('view-all-companies')

class CompanyDetailView(DetailView):
    """
        The following class displays information for a single company within
        Logitrack.
    """

    template_name = 'inventory/companies/company_detail.html'

    def get_object(self):
        company_id = self.kwargs.get("company")
        return get_object_or_404(Company, id=company_id)

class CompanyListView(ListView):
    """
        The following view displays a list of companies within Logitrack
    """
    model = Company
    template_name='inventory/companies/company_list.html'


'''
    Shipment Views

'''

class ShipmentListView(ListView):
    """
        This provides VIEW (list) functionality for all Shipment instances
        within Logitrack for a given company (supplied as a URL parameter)
    """
    model = Shipment
    template_name = 'inventory/shipments/shipment_list.html'

    def get_queryset(self):
        # We only display
        print(self.kwargs['company'])
        self.company = get_object_or_404(Company, id=self.kwargs['company'])
        return Shipment.objects.filter(company=self.company)


class ShipmentCreateView(CreateView):
    """
        The following class allows for the creation of a Shipment instance
        within Logitrack
    """
    template_name = 'inventory/shipments/create_shipment.html'
    form_class = ShipmentCreateForm
    model = Shipment

    def get_success_url(self):
        return reverse('view-all-shipments', kwargs={'company': self.company.id})

    def form_valid(self, form):
        # The shipment is created from a URL that already has the company
        # selected - we need to add the company to the form (which is a required
        # field) so that it's considered to be a valid form
        self.company = get_object_or_404(Company, id=self.kwargs['company'])
        instance = form.save(commit=False)
        instance.company= self.company
        is_valid = super().form_valid(form)
        return is_valid


class ShipmentShipView(UpdateView):
    """
        The following class allows to update an outbound Shipment instance to be
        'shipped'
    """
    template_name = 'inventory/shipments/shipment_ship.html'
    form_class = ShipmentShipForm
    model = Shipment

    pk_url_kwarg='shipmentid'

    def get_initial(self):
        initial = super(UpdateView, self).get_initial()
        initial['date_shipped'] = timezone.now()
        return initial

    def get_context_data(self, *args, **kwargs):
        context = super(ShipmentShipView, self).get_context_data(*args, **kwargs)

        # Display the items on the shipment that is being marked as shipped
        shipmentid = self.kwargs.get("shipmentid")
        shipmentItems = ShipmentItem.objects.filter(shipment=shipmentid)
        context['shipmentItems'] = shipmentItems

        return context

    def form_valid(self, form):
        self.company = get_object_or_404(Company, id=self.kwargs['company'])

        shipment = form.save(commit=False)

        # The is_shipped checkbox is not visible on the form, but the form
        # submission indicates that the shipment was received.
        shipment.is_shipped = True

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('view-all-shipments', kwargs={'company': self.company.id})


class ShipmentReceiveView(UpdateView):
    """
        The following class allows for the updating of an (inbound)
        Shipment instance within Logitrack to be 'received'
    """

    template_name = 'inventory/shipments/shipment_receive.html'
    form_class = ShipmentShipForm
    model = Shipment
    pk_url_kwarg='shipmentid'

    def get_initial(self):
        initial = super(UpdateView, self).get_initial()
        initial['date_shipped'] = timezone.now()
        return initial

    def get_context_data(self, *args, **kwargs):
        context = super(ShipmentReceiveView, self).get_context_data(*args, **kwargs)

        # Display existing shipments to the user, to provide feedback
        # in the event that they try to change the 'is_shippable' property
        # to false when there are pending shipments
        shipmentid = self.kwargs.get("shipmentid")
        shipmentItems = ShipmentItem.objects.filter(shipment=shipmentid)
        context['shipmentItems'] = shipmentItems
        return context

    def form_valid(self, form):
        """
            This overrides the form_valid method of the UpdateView class,
            is order to add to the form data that the shipment was received
        """
        self.company = get_object_or_404(Company, id=self.kwargs['company'])
        shipment = form.save(commit=False)

        # Inbound shipments with is_shipped =True are considered received, which
        # is the desired result for this form submission
        shipment.is_shipped = True
        is_valid = super().form_valid(form)
        return is_valid

    def get_success_url(self):
        return reverse('view-all-shipments', kwargs={'company': self.company.id})



class ShipmentEditItemView(SingleObjectMixin, FormView):
    """
        The following class allows for multiple ShipmentItems to be both
        created and associated to a single Shipment item within Logitrack,
        all on the same page.

    """
    template_name = 'inventory/shipments/add_items_to_shipment.html'
    model = Shipment


    pk_url_kwarg='shipmentid'


    def get_context_data(self, **kwargs):
        """ This function is used to display inventory levels on the form """

        context = super().get_context_data(**kwargs)
        company_id = context['object'].company

        context['items'] = Item.objects.filter(company=company_id)

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Shipment.objects.all())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Shipment.objects.all())
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        """
            This function is used to supply the inlineformset, which is
            imported from inventory/models.py
        """
        return ShipmentItemFormset(**self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return '.'
