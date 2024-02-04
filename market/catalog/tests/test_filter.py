from typing import Dict

from django.template.response import TemplateResponse
from django.test import TestCase, RequestFactory
from django.urls import reverse

from catalog.tests.utils import (
    get_fixtures_list,
    # echo_sql,
)
from catalog.views import CatalogListView


class FilterChecker:
    def check_context_exists(self, response: TemplateResponse) -> Dict:
        object_list = response.context_data["object_list"]
        self.assertTrue(object_list)
        # print(object_list)
        return object_list

    def check_filter_by_name(self, response: TemplateResponse, text: str) -> None:
        self.assertContains(response, text)
        for offer in self.check_context_exists(response):
            self.assertIn(text, offer.product.name + offer.product.about)

    def check_filter_by_price(self, response: TemplateResponse, start_price: float, stop_price: float) -> None:
        for offer in self.check_context_exists(response):
            self.assertTrue(start_price < offer.price < stop_price)

    def check_filter_by_free_delivery(self, response: TemplateResponse) -> None:
        for offer in self.check_context_exists(response):
            self.assertEqual(offer.delivery_method, "FREE")

    def check_filter_by_remains(self, response: TemplateResponse) -> None:
        for offer in self.check_context_exists(response):
            self.assertTrue(offer.remains > 0)

    def check_filter_by_category(self, response: TemplateResponse, category_id: int, category_name: str) -> None:
        self.assertContains(response, category_name)
        for offer in self.check_context_exists(response):
            self.assertEqual(category_id, offer.product.category.pk)

    def check_filter_by_search(self, response: TemplateResponse, text: str) -> None:
        self.assertContains(response, text)
        for offer in self.check_context_exists(response):
            self.assertIn(text, offer.product.name + offer.product.about)


class FilterTest(TestCase, FilterChecker):
    """Тесты фильтра"""

    fixtures = get_fixtures_list()

    def setUp(self) -> None:
        self.factory = RequestFactory()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.path = reverse("catalog:index")

    # @echo_sql
    def test_filter_by_name(self) -> None:
        title = "Aceline"

        params = {"title": title}
        request = self.factory.get(self.path, params)
        request.session = {}
        response: TemplateResponse = CatalogListView.as_view()(request)

        self.check_filter_by_name(response, title)

    # @echo_sql
    def test_filter_by_price(self) -> None:
        start_price = 500_000
        stop_price = 600_000
        price = f"{start_price};{stop_price}"

        params = {"price": price}
        request = self.factory.get(self.path, params)
        response: TemplateResponse = CatalogListView.as_view()(request)

        self.check_filter_by_price(response, start_price, stop_price)

    # @echo_sql
    def test_filter_by_name_price(self) -> None:
        title = "Hisense"
        start_price = 500_000
        stop_price = 600_000
        price = f"{start_price};{stop_price}"

        params = {"price": price, "title": title}
        request = self.factory.get(self.path, params)
        request.session = {}
        response: TemplateResponse = CatalogListView.as_view()(request)

        self.check_filter_by_name(response, title)
        self.check_filter_by_price(response, start_price, stop_price)

    # @echo_sql
    def test_filter_by_name_price_free_delivery(self) -> None:
        title = "Notebook"
        start_price = 35_000
        stop_price = 40_000
        price = f"{start_price};{stop_price}"

        params = {"price": price, "title": title, "free_delivery": True}
        request = self.factory.get(self.path, params)
        request.session = {}
        response: TemplateResponse = CatalogListView.as_view()(request)

        self.check_filter_by_name(response, title)
        self.check_filter_by_free_delivery(response)
        self.check_filter_by_price(response, start_price, stop_price)

    # @echo_sql
    def test_filter_by_name_price_free_delivery_remains(self) -> None:
        title = "Notebook"
        start_price = 35_000
        stop_price = 40_000
        price = f"{start_price};{stop_price}"

        params = {"price": price, "title": title, "free_delivery": True, "remains": True}
        request = self.factory.get(self.path, params)
        request.session = {}
        response: TemplateResponse = CatalogListView.as_view()(request)

        self.check_filter_by_name(response, title)
        self.check_filter_by_free_delivery(response)
        self.check_filter_by_remains(response)
        self.check_filter_by_price(response, start_price, stop_price)

    # @echo_sql
    def test_filter_by_name_price_free_delivery_remains_category(self) -> None:
        title = "Notebook"
        start_price = 35_000
        stop_price = 40_000
        price = f"{start_price};{stop_price}"
        category_id = 3
        category_name = "Ноутбуки"

        params = {
            "price": price,
            "title": title,
            "free_delivery": True,
            "remains": True,
            "category_id": category_id,
        }
        request = self.factory.get(self.path, params)
        request.session = {}
        response: TemplateResponse = CatalogListView.as_view()(request)

        self.check_filter_by_name(response, title)
        self.check_filter_by_free_delivery(response)
        self.check_filter_by_remains(response)
        self.check_filter_by_category(response, category_id, category_name)
        self.check_filter_by_price(response, start_price, stop_price)

    # @echo_sql
    def test_filter_by_free_delivery(self) -> None:
        params = {"free_delivery": True}
        request = self.factory.get(self.path, params)
        response: TemplateResponse = CatalogListView.as_view()(request)
        self.check_filter_by_free_delivery(response)

    # @echo_sql
    def test_filter_by_remains(self) -> None:
        params = {"remains": True}
        request = self.factory.get(self.path, params)
        response: TemplateResponse = CatalogListView.as_view()(request)
        self.check_filter_by_remains(response)

    # @echo_sql
    def test_filter_by_tags(self) -> None:
        tag_id = 16

        params = {"tag_id": tag_id}
        request = self.factory.get(self.path, params)
        response: TemplateResponse = CatalogListView.as_view()(request)

        for offer in self.check_context_exists(response):
            self.assertIn(tag_id, [tag.pk for tag in offer.product.tags.all()])

    # @echo_sql
    def test_filter_by_category(self) -> None:
        category_id = 15
        category_name = "Аксессуары"

        params = {"category_id": category_id}
        request = self.factory.get(self.path, params)
        request.session = {}
        response: TemplateResponse = CatalogListView.as_view()(request)
        self.check_filter_by_category(response, category_id, category_name)

    # @echo_sql
    def test_search(self) -> None:
        search = "Watch"

        params = {"search": search}
        request = self.factory.get(self.path, params)
        request.session = {}
        response: TemplateResponse = CatalogListView.as_view()(request)
        self.check_filter_by_search(response, search)

    # @echo_sql
    def test_search_with_category(self) -> None:
        category_id = 15
        category_name = "Аксессуары"
        search = "Watch"

        params = {"category_id": category_id, "search": search}
        request = self.factory.get(self.path, params)
        request.session = {}
        response: TemplateResponse = CatalogListView.as_view()(request)

        self.check_filter_by_search(response, search)
        self.check_filter_by_category(response, category_id, category_name)
