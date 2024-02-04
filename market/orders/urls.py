from django.urls import path

from orders.views import (
    OrderDetailView,
    OrderStepOneView,
    OrderStepTwoView,
    OrderStepThreeView,
    OrderHistoryListView,
    OrderStepFourView,
)

app_name = "orders"


urlpatterns = [
    path("step_one/", OrderStepOneView.as_view(), name="view_step_one"),
    path("step_two/", OrderStepTwoView.as_view(), name="view_step_two"),
    path("step_three/", OrderStepThreeView.as_view(), name="view_step_three"),
    path("step_four/", OrderStepFourView.as_view(), name="view_step_four"),
    path("history/", OrderHistoryListView.as_view(), name="history"),
    path("detail/<int:pk>/", OrderDetailView.as_view(), name="detail_order"),
]
