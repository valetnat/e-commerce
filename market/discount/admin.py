from django.contrib import admin  # noqa F401
from .models import SetPromo, ProductPromo, CartPromo, ProductCategorySet


@admin.register(ProductPromo)
class ProductPromoAdmin(admin.ModelAdmin):
    """Админ Скидка на товар."""

    list_display = ("pk", "name", "value", "weight", "active_from", "active_to", "is_active")
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)


@admin.register(SetPromo)
class SetPromoAdmin(admin.ModelAdmin):
    """Админ Скидка на набор."""

    list_display = ("pk", "name", "value", "weight", "active_from", "active_to", "is_active")
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)


@admin.register(CartPromo)
class CartPromoAdmin(admin.ModelAdmin):
    """Админ скида на корзину."""

    list_display = ("pk", "name", "value", "weight", "active_from", "active_to", "is_active")
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)


@admin.register(ProductCategorySet)
class ProductCategorySetAdmin(admin.ModelAdmin):
    """Админ Наборы."""

    list_display = (
        "pk",
        "name",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)
