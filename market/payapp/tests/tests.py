from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from orders.models import Order
from ..forms import BancAccountForm
from ..models import OrderPayStatus
from catalog.tests.utils import get_fixtures_list


class PayAppFormTest(TestCase):
    def test_valid_banc_account_form(self):
        data = {"banc_account": "1234 1234"}
        form = BancAccountForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_banc_account_form(self):
        data = {"banc_account": "1234qwe1234"}
        form = BancAccountForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_banc_account_form_case_1(self):
        data = {"banc_account": "12311234"}
        form = BancAccountForm(data=data)
        self.assertFalse(form.is_valid())


class PayappOrderPayStatusTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
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
            "total_price": "120400.85",
        }
        cls.order = Order.objects.create(**some_data)

    def test_create_model(self):
        (model := OrderPayStatus(order=self.order)).save()
        queryset = OrderPayStatus.objects.all()
        self.assertIn(model, queryset)

    def test_verbose_name(self):
        (model := OrderPayStatus(order=self.order)).save()
        field_verboses = {
            "answer_from_api": "ответ сервиса оплаты",
            "created_at": "дата выполнения",
            "order": "заказ",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(model._meta.get_field(field).verbose_name, expected_value)


class TestOrder(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
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
            "total_price": "120400.85",
        }
        cls.order = Order.objects.create(**some_data)

    def test_Order_have_fields(self):
        params = dir(self.order)
        fields = ("STATUS_CREATED", "STATUS_PAID", "STATUS_NOT_PAID", "status")
        for field in fields:
            with self.subTest():
                self.assertIn(field, params)


class AppPayViewsTest(TestCase):
    fixtures = get_fixtures_list()

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
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
            "total_price": "120400.85",
        }
        cls.order = Order.objects.create(**some_data)
        cls.order.save()

    def test_PayView(self):
        url = reverse("payapp:order_pay", kwargs={"order_pk": self.order.pk})
        response = self.client.get(url)
        self.assertContains(response, text="Оплата")

    def test_PayView_other_account(self):
        self.order.payment_type = "random"
        self.order.save()
        url = reverse("payapp:order_pay", kwargs={"order_pk": self.order.pk})
        response = self.client.get(url)
        self.assertContains(response, text="Сгенирировать случайный счет")

    def test_PayStatusView_pai_status(self):
        self.order.status = Order.STATUS_PAID
        self.order.save()
        OrderPayStatus(order=self.order, answer_from_api={"successfully": True, "error": ""}).save()
        url = reverse("payapp:status", kwargs={"pk": self.order.pk})
        response = self.client.get(url)
        self.assertContains(response, text="OK")

    def test_PayStatusView_not_pai_status(self):
        self.order.status = Order.STATUS_NOT_PAID
        self.order.save()
        OrderPayStatus(order=self.order, answer_from_api={"successfully": False, "error": "Some error"}).save()
        url = reverse("payapp:status", kwargs={"pk": self.order.pk})
        response = self.client.get(url)
        self.assertContains(response, text="Some error")

    def test_PayStatusView_wait_status(self):
        self.order.status = Order.STATUS_NOT_PAID
        self.order.save()
        OrderPayStatus(order=self.order).save()
        url = reverse("payapp:status", kwargs={"pk": self.order.pk})
        response = self.client.get(url)
        self.assertContains(response, text="Ожидание")
