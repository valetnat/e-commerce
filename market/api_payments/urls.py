from django.urls import path

from .views import (
    megano_fake_pay,
)

app_name = "api_payments"

urlpatterns = [path("meganopays/", megano_fake_pay, name="pays")]
