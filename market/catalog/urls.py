from django.urls import path

from .views import CatalogHomeView

app_name = "catalog"

urlpatterns = [
    path("", CatalogHomeView.as_view(), name="index"),
]
