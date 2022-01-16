from django.urls import path, include

urlpatterns = [
    path('', views.landing_page, name="landing_page")
]
