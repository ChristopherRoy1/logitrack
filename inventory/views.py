from django.shortcuts import render
from .models import Item
from django.views.generic.edit import CreateView, UpdateView, DeleteView
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



class ItemCreateView(CreateView):
    template_name = 'inventory/items/item_create.html'
    form_class = ItemCreateForm
    model = Item
    
