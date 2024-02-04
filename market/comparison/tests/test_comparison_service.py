from django.test import TestCase
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from catalog.tests.utils import get_fixtures_list

from comparison.services import ComparisonService
from products.models import Product, Category, Detail, Manufacturer


existing_comparison = {
    "1": {
        "details": {"test detail_1": "test_value_1", "test detail_2": "test_value_2", "test detail_3": "test_value_3"},
        "name": "test_name",
        "category": "test_category",
        "preview": "/test/path/to/preview/test.png",
        "created_at": "2023-10-11 08:47:55.699555+00:00",
    },
    "2": {
        "details": {
            "test detail_1": "test_value_1",
            "test detail_2": "test_value_2",
            "test detail_4": "test_value_4",
            "test detail_5": "test_value_5",
        },
        "name": "test_name",
        "category": "test_category",
        "preview": "/test/path/to/preview/test.png",
        "created_at": "2023-10-11 08:47:55.699555+00:00",
    },
}


class ComparisonServiceInitializeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self) -> None:
        self.request = RequestFactory().get("/")

        # add session to request
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(self.request)
        self.request.session.save()

    def test_initialize_comparison_clean_session(self):
        request = self.request
        comparison = ComparisonService(request)
        self.assertEqual(comparison.comparison, {})

    def test_initialize_comparison_filled_session(self):
        request = self.request
        request.session["comparison"] = existing_comparison
        comparison = ComparisonService(request)
        self.assertEqual(comparison.comparison, existing_comparison)


class ComparisonServiceAddDeleteTestCase(TestCase):
    fixtures = get_fixtures_list()

    @classmethod
    def setUpTestData(cls):
        cls.product_1 = Product.objects.get(pk=3)
        cls.product_2 = Product.objects.get(pk=1)
        cls.product_3 = Product.objects.get(pk=5)

    def setUp(self) -> None:
        self.request = RequestFactory().get("/")

        # add session to request
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(self.request)
        self.request.session["comparison"] = existing_comparison
        self.request.session.save()

    def test_comparison_add_product_successfully(self):
        """
        Успешное добавление товара в список сравнения.
        """
        comparison = ComparisonService(self.request)
        comparison.add(self.product_1)

        self.assertEqual(len(comparison.comparison), 3)

    def test_comparison_add_product_failed(self):
        """
        Добаление существующего товара в списоке сравнения.
        """
        comparison = ComparisonService(self.request)
        comparison.add(self.product_2)

        self.assertEqual(len(comparison.comparison), 2)

    def test_comparison_remove_product_successfully(self):
        """
        Успешное удаление товара из список сравнения.
        """
        comparison = ComparisonService(self.request)
        comparison.remove(self.product_2)

        self.assertEqual(len(comparison.comparison), 2)

    def test_comparison_remove_product_failed(self):
        """
        Удаление товара, которого нет в списоке сравнения.
        """
        comparison = ComparisonService(self.request)
        comparison.remove(self.product_3)

        self.assertEqual(len(comparison.comparison), 3)


class ComparisonServiceOtherCase(TestCase):
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

    def setUp(self) -> None:
        self.request = RequestFactory().get("/")

        # add session to request
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(self.request)
        self.request.session["comparison"] = {}
        self.request.session.save()

    def test_get_valid_products_list_length(self):
        comparison = ComparisonService(self.request)
        comparison.add(self.product_1)
        comparison.add(self.product_2)
        valid_list = comparison.get_valid_products_list()
        self.assertEqual(len(valid_list.keys()), 2)

    def test_get_all_unique_details(self):
        """
        Получение всех уникальных характеристик продуктов из списка сравнения.
        """
        comparison = ComparisonService(self.request)
        comparison.add(self.product_1)
        comparison.add(self.product_2)
        valid_list = comparison.get_valid_products_list()
        products_list = comparison.get_all_unique_details(valid_list)
        self.assertEqual(
            products_list,
            sorted(
                [
                    "тестовая_характеристика_1",
                    "тестовая_характеристика_2",
                    "тестовая_характеристика_3",
                    "тестовая_характеристика_4",
                    "тестовая_характеристика_5",
                ]
            ),
        )

    def test_get_common_diff_details(self):
        """
        Проверка общ. и отл. характеристик продуктов из списка сравнения.
        """
        comparison = ComparisonService(self.request)
        comparison.add(self.product_1)
        comparison.add(self.product_2)
        common, diff = comparison.get_common_diff_details(
            sorted(
                [
                    "тестовая_характеристика_1",
                    "тестовая_характеристика_2",
                    "тестовая_характеристика_3",
                    "тестовая_характеристика_4",
                    "тестовая_характеристика_5",
                ]
            ),
            comparison.comparison,
        )

        self.assertEquals(common, ["тестовая_характеристика_1"])
        self.assertEqual(
            diff,
            [
                "тестовая_характеристика_2",
                "тестовая_характеристика_3",
                "тестовая_характеристика_4",
                "тестовая_характеристика_5",
            ],
        )

    def test_each_product_has_all_unique_details(self):
        comparison = ComparisonService(self.request)
        comparison.add(self.product_1)
        comparison.add(self.product_2)
        result = comparison.compare(
            sorted(
                [
                    "тестовая_характеристика_1",
                    "тестовая_характеристика_2",
                    "тестовая_характеристика_3",
                    "тестовая_характеристика_4",
                    "тестовая_характеристика_5",
                ]
            ),
            comparison.comparison,
        )

        for expected_value in result.values():
            with self.subTest(expected_value=expected_value.get("detail")):
                self.assertEqual(len(expected_value), 5)
