from django.contrib import admin

from .models import Shop, Offer


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """Административная панель модели: Магазин"""

    list_display = (
        "pk",
        "name",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Административная панель модели: Предложение"""

    list_display = (
        "pk",
        "shop",
        "product",
        "price",
        "remains",
    )
    list_display_links = (
        "pk",
        "price",
    )
    ordering = (
        "pk",
        "price",
    )
    search_fields = ["product", "shop"]
