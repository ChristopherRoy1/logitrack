from django.urls import path, include, reverse
from . import views
from .models import Item

urlpatterns = [
    path('', views.landing_page, name="landing_page"),
    path('view-all-items/', views.view_all_items, name="view_all_items"),
    path('create-item/', views.ItemCreateView.as_view(model=Item, success_url='/view-all-items/'), name='create_item'),
    path('item/<int:id>', views.ItemDetailView.as_view(), name="view-item"),
    path('item/<int:id>/edit/', views.ItemUpdateView.as_view(), name="edit-item"),
    path('item/<int:id>/delete/', views.ItemDeleteView.as_view(model=Item, success_url='/view-all-items/'), name="delete-item"),

    path('view-all-companies/', views.CompanyListView.as_view(), name="view-all-companies"),
    path('create-company/', views.CompanyCreateView.as_view(), name='create-company'),
    path('company/<int:company>', views.CompanyDetailView.as_view(), name='view-company'),


    path('company/<int:company>/shipments/', views.ShipmentListView.as_view(), name="view-all-shipments"),
    path('company/<int:company>/shipments/create/', views.ShipmentCreateView.as_view(), name="create-shipment"),
    path('company/<int:company>/shipments/<int:shipmentid>/items/', views.ShipmentEditItemView.as_view(), name="edit-shipment"),
]
