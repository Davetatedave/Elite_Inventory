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
    path("updateGrade/", views.updateGrade, name="updateGrade"),
    path("BMlistingsajax/", views.BMlistingsajax, name="BMlistingsajax"),
    path("updateBMquantity/", views.updateBMquantity, name="updateBMquantity"),
    path("getBMdata/", views.getBMdata, name="getBMdata"),
    path("add_stock/", views.addStock, name="add_stock"),
    path("add_stock/imeis", views.addStockImeis, name="add_stock_imeis"),
    path("sales/getBmOrders", views.getBmOrders, name="getBmOrders"),
    path("salesajax/", views.salesajax, name="salesAjax"),
    path("sales/detail/<int:pk>", views.orderDetail.as_view(), name="orderDetail"),
    path("shipping_rates/", views.getShippingRates, name="get_shipping_rates"),
    path("shipping_label/", views.buyShippingLabel, name="buyShippingLabel"),
    path(
        "shipment_details/<int:shipment_id>",
        views.shipmentDetails,
        name="shipmentDetails",
    ),
    path(
        "listings/resolve_marketplace_sku/<int:pk>",
        views.resolveMarketplaceSku.as_view(),
        name="resolveMarketplaceSku",
    ),
    path("new_sku/", views.newSKU, name="newSKU"),
    path("update_address/", views.updateAddress, name="updateAddress"),
    path("sales/get_label/<int:so>", views.get_label, name="get_label"),
    path("commit_imei/", views.commitImei, name="commitImei"),
    path("remove_imei/", views.removeImei, name="removeImei"),
]
