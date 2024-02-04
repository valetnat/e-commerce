from django.urls import path

from .views import PayView, PayStatusView, BankAccountValidate


app_name = "payapp"

urlpatterns = [
    path("order/<int:order_pk>/", PayView.as_view(), name="order_pay"),
    path("status/<int:pk>/", PayStatusView.as_view(), name="status"),
    path("account_validate/<int:order_pk>/", BankAccountValidate.as_view(), name="account_validate"),
]
