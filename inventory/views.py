from django.shortcuts import render
from .models import Item

# Create your views here.
def landing_page(request):
    items = Item.objects.all()

    context = {
        'items': items
    }

    return render(request, 'home.html', context=context)
