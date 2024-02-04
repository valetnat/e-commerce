from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from catalog.tests.utils import get_fixtures_list
from orders.models import Order

User = get_user_model()


class OrderCreateTest(TestCase):
    """Тест создания заказа"""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            email="test_user@mail.com",
            username="test_user",
            password="qwerty1234",
        )

        some_data = {
            "user": cls.user,
            "city": "test city",
            "address": "test address",
            "delivery_type": "Новый заказ",
            "payment_type": "картой",
            "order_number": 1,
            "status": "created",
            "total_price": "45888.65",
        }
        cls.order = Order.objects.create(**some_data)

    def setUp(self) -> None:
        self.client.login(email="test_user@mail.com", password="qwerty1234")

    def test_create_order(self):
        order = Order.objects.last()
        self.assertEqual(self.order.order_number, 1)
        self.assertEqual(self.order.user.username, "test_user")
        self.assertEqual(self.order.payment_type, "картой")
        self.assertEqual(self.order.payment_type, order.payment_type)
        self.assertTrue(self.order.total_price, "45888.65")


class UserHistoryOrdersListViewTest(TestCase):
    """Тест истории заказов пользователя"""

    fixtures = get_fixtures_list()

    @classmethod
    def setUpTestData(cls):
        cls.all_info = {
            "username": "John-test",
            "phone": "89701112233",
            "residence": "London",
            "address": "Bakers streets 148 ap.3",
            "retailer_group": True,
        }
        cls.user_login_info = {
            "email": "jhon@test.com",
            "password": "JohnTest1234",
        }
        # Создание пользователя
        cls.user = User.objects.create_user(
            username=cls.all_info["username"],
            email=cls.user_login_info["email"],
            password=cls.user_login_info["password"],
            phone=cls.all_info["phone"],
            residence=cls.all_info["residence"],
            address=cls.all_info["address"],
        )

        cls.order_data = {
            "user": cls.user,
            "city": "test city",
            "address": "test address",
            "delivery_type": "usually",
            "payment_type": "card",
            "order_number": 1,
            "status": "created",
            "total_price": "12365.88",
        }
        # Создание заказа
        cls.order = Order.objects.create(**cls.order_data)

    def setUp(self) -> None:
        self.client.login(**self.user_login_info)

    # @echo_sql
    def test_order_contains_delivery_type(self):
        response = self.client.get(reverse("orders:history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "обычная доставка")

    def test_contains_payment_type(self):
        response = self.client.get(reverse("orders:history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "онлайн картой")

    def test_contains_order_number(self):
        response = self.client.get(reverse("orders:history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.order_number)


class OrderDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.all_info = {
            "username": "John-test",
            "phone": "89701112233",
            "residence": "London",
            "address": "Bakers streets 148 ap.3",
            "retailer_group": True,
        }
        cls.user_login_info = {
            "email": "jhon@test.com",
            "password": "JohnTest1234",
        }
        cls.user = User.objects.create_user(
            username=cls.all_info["username"],
            email=cls.user_login_info["email"],
            password=cls.user_login_info["password"],
            phone=cls.all_info["phone"],
            residence=cls.all_info["residence"],
            address=cls.all_info["address"],
        )

        cls.order_data = {
            "user": cls.user,
            "city": "test city",
            "address": "test address",
            "delivery_type": "usually",
            "payment_type": "card",
            "order_number": 1,
            "status": "created",
            "total_price": "12365.88",
        }
        cls.order = Order.objects.create(**cls.order_data)

    def setUp(self) -> None:
        self.client.login(**self.user_login_info)

    def test_detail_order(self):
        url = reverse("orders:detail_order", kwargs={"pk": self.order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contains_order_info(self):
        url = reverse("orders:detail_order", kwargs={"pk": self.order.pk})
        response = self.client.get(url)
        self.assertContains(response, "test city")
        self.assertContains(response, "test address")
        self.assertContains(response, "12365.88")

    def test_payment_method(self):
        url = reverse("orders:detail_order", kwargs={"pk": self.order.pk})
        response = self.client.get(url)
        self.assertContains(response, "cart")
