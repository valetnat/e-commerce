from django.urls import path
from .views import DiscountListView, SetPromoView, CartPromoView, ProductPromoView

app_name = "discount"

urlpatterns = [
    path("", DiscountListView.as_view(), name="discount-list"),
    path("setpromo/<int:pk>", SetPromoView.as_view(), name="setpromo"),
    path("cartpromo/<int:pk>", CartPromoView.as_view(), name="cartpromo"),
    path("productpromo/<int:pk>", ProductPromoView.as_view(), name="productpromo"),
]
