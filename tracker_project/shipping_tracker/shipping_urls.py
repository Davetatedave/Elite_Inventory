from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("shipping/", views.shipping, name="shipping"),
    path(route="<int:pk>/", view=views.ShippingDetailView.as_view(), name="detail"),
    path("phoneCheck/", views.phoneCheck, name="phoneCheck"),
    path("inventory/", views.inventory, name="inventory"),
    path("inventory2/", views.inventory2, name="inventory2"),
]
