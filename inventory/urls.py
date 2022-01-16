from django.urls import path, include, reverse
from . import views
from .models import Item

urlpatterns = [
    path('', views.landing_page, name="landing_page"),
    path('view-all-items/', views.view_all_items, name="view_all_items"),
    path('item/<int:id>', views.ItemDetailView.as_view(), name="view-item"),
    path('item/<int:id>/edit/', views.ItemUpdateView.as_view(), name="edit-item"),
    path('item/<int:id>/delete/', views.ItemDeleteView.as_view(model=Item, success_url='/view-all-items/'), name="delete-item"),
    path('create-item/', views.ItemCreateView.as_view(model=Item, success_url='/view-all-items/'), name='create_item'),
]
