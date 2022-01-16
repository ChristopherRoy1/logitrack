from django.shortcuts import render, get_object_or_404
from .models import Item
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from .forms import ItemCreateForm

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
        # TODO: impose view-specific validation
        return super().form_valid(form)


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
