from django.urls import path, include, reverse
from . import views
from .models import Item

urlpatterns = [
    path('', views.landing_page, name="landing_page"),
    path('view-all-items/', views.view_all_items, name="view_all_items"),
    path('create-item/', views.ItemCreateView.as_view(model=Item, success_url="/view-all-items/"), name='create_item'),
]
