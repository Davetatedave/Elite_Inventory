from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("shipping/", views.shipping, name="shipping"),
    path(
        route="inventory2/detail/<int:pk>/",
        view=views.deviceDetail.as_view(),
        name="detail",
    ),
    path("phoneCheck/", views.phoneCheck, name="phoneCheck"),
    path("inventory/", views.inventory, name="inventory"),
    path("inventory2/", views.inventory2, name="inventory2"),
    path("inventoryajax/", views.inventoryAjax, name="inventoryAjax"),
    path("deletedevices/", views.deleteDevices, name="deleteDevices"),
    path("updateStatus/", views.updateStatus, name="updateStatus"),
]
