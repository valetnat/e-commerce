from decimal import Decimal

from django.db import transaction
from orders.models import Order, OrderDetail
from profiles.models import User
from shops.models import Offer
from config import settings
from django.db.models import F, Sum
from discount.services import CartDiscount
from cart.services.cart_service import AnonimCartService


class OrderServices:
    def __init__(self, request):
        self.request = request

    def get_last_order(self) -> Order:
        return Order.objects.filter(carts__user_user_id=self.request.pk)


class OrderDetailCreate:
    """Клас для работы с заказами"""

    def __init__(self, request):
        self.user = request.user
        self.request = request
        self.session = request.session.get(settings.CART_SESSION_KEY)
        self.cart_service = AnonimCartService(request)

    def get_products_in_cart(self):
        """Показать продукты, которые находятся в корзине в сессиях"""

        multiselect = self.session.keys()
        products = Offer.objects.filter(pk__in=multiselect)
        return products

    def create_order(self):
        """Метод создания заказа после прохождения форм опроса пользователя"""

        user = User.objects.filter(pk=self.request.user.pk).first()
        delivery_type = self.request.session["delivery_type"]
        city = self.request.session["city"]
        address = self.request.session["address"]
        payment_type = self.request.session["payment_type"]

        discount_service = CartDiscount(self.cart_service)
        discount = discount_service.get_discount()
        total_price = round((Decimal(self.cart_service.get_upd_price()) - Decimal(discount["sale"])), 2)

        order = Order.objects.create(
            city=city,
            address=address,
            user=user,
            delivery_type=delivery_type,
            order_number=self.get_last_order_number(),
            payment_type=payment_type,
            status=Order.STATUS_CREATED,
            total_price=total_price,
            discount_amount=discount["sale"],
        )
        return order

    def get_last_order_number(self):
        """
        Метод получает последний номер заказа пользователя.
        Присваивает следующий порядковый номер созданному заказу.
        # В разработке...
        """
        user = User.objects.get(pk=self.request.user.pk)
        last_client_order = Order.objects.filter(user=user).first()
        if last_client_order is None:
            order_number = 1
            return order_number

        order_number = last_client_order.order_number + 1
        return order_number

    @transaction.atomic
    def created_order_details_product(self):
        """
        Метод добавления продуктов из корзины.
        Переменная order - создаёт новый заказ и привязывает предложения к этому заказу.
        """

        # Заказ создаётся здесь
        order = self.create_order()

        for offer, value in self.session.items():
            if value == 0:
                continue
            add_offer = Offer.objects.get(pk=offer)
            add_offer.remains -= int(value)
            add_offer.save()
            OrderDetail.objects.create(offer=add_offer, quantity=value, user_order=order)


def get_order_total_price(order: Order):
    total_price = (
        OrderDetail.objects.filter(user_order=order)
        .select_related("offer")
        .annotate(sum_price=(F("quantity") + 0) * F("offer__price"))
        .aggregate(Sum("sum_price"))
        .get("sum_price__sum")
    )
    return total_price
