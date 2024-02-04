from django.urls import path

from .views import HomeView, ProductView

app_name = "products"

urlpatterns = [
    path("", HomeView.as_view(), name="home-page"),
    path("product/<int:pk>/", ProductView.as_view(), name="product-detail"),
]
