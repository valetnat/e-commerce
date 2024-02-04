from django.urls import path

from .views import ComparisonTemplateView, ComparisonAddView, ComparisonDeleteView


app_name = "comparison"

urlpatterns = [
    path("", ComparisonTemplateView.as_view(), name="comparison"),
    path("add/", ComparisonAddView.as_view(), name="comparison_add"),
    path("del/", ComparisonDeleteView.as_view(), name="comparison_delete"),
]
