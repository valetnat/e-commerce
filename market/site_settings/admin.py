from django.contrib import admin

from site_settings.models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Админка настроек сайта"""

    change_form_template = "settings/settings.html"

    list_display = (
        "pk",
        "default_price_from",
        "default_price_to",
        "default_sort",
        "default_sort_type",
        "default_sort_desc",
        "paginate_by",
        "pagination_on_each_side",
        "pagination_on_ends",
        "categories_list_cache_timeout",
    )
