from django.contrib import admin
from orders.models import Order, OrderDetail


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "created_at",
        "city",
        "address",
    ]


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ["pk", "offer_name", "quantity"]
    list_display_links = ["pk", "offer_name"]

    def offer_name(self, obj: OrderDetail):
        product_name = obj.offer.product.name
        return product_name
