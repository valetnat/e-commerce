from django.test import TestCase
from django.contrib.auth import get_user_model

from catalog.tests.utils import get_fixtures_list, echo_sql  # noqa
from orders.models import Order, OrderDetail
from shops.models import Offer


User = get_user_model()


class OrderDetailModelTest(TestCase):
    """Тест модели деталей заказа"""

    fixtures = get_fixtures_list()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.get(pk=2)
        cls.offer = Offer.objects.get(pk=2)
        order_data = {
            "user": cls.user,
            "city": "test city",
            "address": "test address",
            "delivery_type": "Новый заказ",
            "payment_type": "картой",
            "status": "created",
            "total_price": "56000.00",
        }
        cls.order = Order.objects.create(**order_data)
        cls.order_detail = OrderDetail.objects.create(offer=cls.offer, quantity=2, user_order=cls.order)

    def test_details(self):
        order_detail = OrderDetailModelTest.order_detail

        field_verboses = {
            "offer": "Предложение",
            "quantity": "Количество товара",
            "user_order": "Номер заказа пользователя",
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(order_detail._meta.get_field(field).verbose_name, expected_value)

    def test_default_value(self):
        order_detail = OrderDetailModelTest.order_detail
        default = order_detail._meta.get_field("quantity").default
        self.assertEqual(default, 1)


class OrderModelTest(TestCase):
    """Тест модели заказа."""

    fixtures = get_fixtures_list()

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(pk=2)
        cls.order = Order.objects.create(
            city="Test city",
            address="Test address for model",
            user=cls.user,
            total_price="12345.54",
        )

    def test_details(self):
        order = OrderModelTest.order
        field_verboses = {
            "created_at": "дата создания заказа",
            "city": "Город доставки",
            "address": "адрес доставки",
            "user": "user",
            "delivery_type": "метод доставки",
            "payment_type": "способ оплаты",
            "order_number": "номер заказа",
            "status": "status",
            "total_price": "общая стоимость",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(order._meta.get_field(field).verbose_name, expected_value)

    def test_default_delivery_type(self):
        order = OrderModelTest.order
        default = order._meta.get_field("delivery_type").default
        self.assertEqual(default, "usually")

    def test_default_payment_type(self):
        order = OrderModelTest.order
        default = order._meta.get_field("payment_type").default
        self.assertEqual(default, "card")

    def test_default_order_number(self):
        order = OrderModelTest.order
        default = order._meta.get_field("order_number").default
        self.assertEqual(default, 1)

    def test_default_order_status(self):
        order = OrderModelTest.order
        default = order._meta.get_field("status").default
        self.assertEqual(default, "создан")
