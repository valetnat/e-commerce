from importlib import import_module

from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.test.client import RequestFactory

from comparison.services import ComparisonService
from products.models import Product, Category, Detail, Manufacturer


class SessionBuilder:
    def build_session(self):
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store


class ComparisonDeleteViewTestCase(SessionBuilder, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Тестовая категория")
        cls.manufacturer = Manufacturer.objects.create(name="tecтовый производитель")
        cls.details_1 = Detail.objects.bulk_create(
            [
                Detail(name="тестовая_характеристика_1"),
                Detail(name="тестовая_характеристика_2"),
                Detail(name="тестовая_характеристика_3"),
            ]
        )
        cls.details_2 = Detail.objects.bulk_create(
            [
                Detail(name="тестовая_характеристика_1"),
                Detail(name="тестовая_характеристика_4"),
                Detail(name="тестовая_характеристика_5"),
            ]
        )

        cls.product_1 = Product.objects.create(
            name="Тестовый продукт", category=cls.category, manufacturer=cls.manufacturer
        )

        cls.product_1.details.set([*cls.details_1], through_defaults={"value": "тестовое значение"})

        cls.product_2 = Product.objects.create(
            name="Тестовый продукт 2", category=cls.category, manufacturer=cls.manufacturer
        )

        cls.product_2.details.set([*cls.details_2], through_defaults={"value": "тестовое значение 2"})

    def setUp(self):
        self.request = RequestFactory()
        self.path = reverse("comparison:comparison_delete")
        self.build_session()
        self.session[settings.COMPARISON_SESSION_ID] = {}
        self.session.save()

    def test_product_deletion(self):
        self.session[settings.COMPARISON_SESSION_ID] = {str(self.product_1.pk): {}}
        self.session.save()

        # Create a mock request with session data
        request = self.request.post(self.path)
        request.session = self.session

        comparison = ComparisonService(request=request)
        comparison.remove(product=self.product_1)

        self.assertEqual(self.session.get(settings.COMPARISON_SESSION_ID), {})

    def test_session_clear(self):
        self.session[settings.COMPARISON_SESSION_ID] = {str(self.product_1.pk): {}, str(self.product_2.pk): {}}
        self.session.save()

        # Create a mock request with session data
        request = self.request.get(self.path)
        request.session = self.session

        comparison = ComparisonService(request=request)
        comparison.clear()

        self.assertEqual(self.session.get(settings.COMPARISON_SESSION_ID), None)


class ComparisonDeleteViewRedirectTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.path = reverse("comparison:comparison_delete")

    def test_view_success_url_redirect_get(self):
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, 302)

    def test_view_success_url_redirect_post(self):
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, 302)
