from django.urls import path

from .views import ImportView


app_name = "importdata"

urlpatterns = [
    path("", ImportView.as_view(), name="importdata"),
]
