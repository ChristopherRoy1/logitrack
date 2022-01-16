from django.shortcuts import render
from .models import Item

# Create your views here.
def landing_page(request):
    items = Item.objects.all()

    context = {
        'items': items,
        'itemCount': items.count()
    }

    return render(request, 'inventory/home.html', context=context)
