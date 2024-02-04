from django.urls import path

from site_settings.views import clear_all_cache_view

app_name = "site_settings"

urlpatterns = [
    path("clear_all_cache", clear_all_cache_view, name="clear_all_cache"),
]
