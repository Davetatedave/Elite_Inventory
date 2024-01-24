from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.index, name="home"),
    path("shipping/", views.shipping, name="shipping"),
    path(
        route="inventory2/detail/<int:pk>/",
        view=views.deviceDetail.as_view(),
        name="detail",
    ),
    path("phoneCheck/", views.phoneCheck, name="phoneCheck"),
    path("inventory/", views.inventory, name="inventory"),
    path("sales/", views.sales, name="sales"),
    path("listings/", views.listings, name="listings"),
    path("inventoryajax/", views.inventoryAjax, name="inventoryAjax"),
    path("deletedevices/", views.deleteDevices, name="deleteDevices"),
    path("updateStatus/", views.updateStatus, name="updateStatus"),
    path("BMlistingsajax/", views.BMlistingsajax, name="BMlistingsajax"),
    path("updateBMquantity/", views.updateBMquantity, name="updateBMquantity"),
]
