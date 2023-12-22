from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("test/", views.test_index, name="test_index"),
    path(route="<int:pk>/", view=views.ShippingDetailView.as_view(), name="detail"),
]


