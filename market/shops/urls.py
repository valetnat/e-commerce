from django.urls import path

from .views import (
    hello_shop_view,
    ShopDetailsView,
    ShopProductsDetail,
    ShopUpdateView,
)

app_name = "shops"

urlpatterns = [
    path("", hello_shop_view, name="hello"),
    path("<int:pk>/", ShopDetailsView.as_view(), name="shop_detail"),
    path("<int:pk>/products/", ShopProductsDetail.as_view(), name="shop_products"),
    path("<int:pk>/update/", ShopUpdateView.as_view(), name="shop-update"),
]
