from typing import List

from django.template.response import TemplateResponse
from django.test import TestCase, RequestFactory
from django.urls import reverse

from catalog.tests.utils import (
    get_fixtures_list,
    # echo_sql,
)
from catalog.views import CatalogListView


class SortChecker:
    def check_sort(self, result: List, desc: bool = False) -> None:
        self.assertTrue(result)
        sorted_result = sorted(result, reverse=desc)
        self.assertTrue(result == sorted_result)


class SortTest(TestCase, SortChecker):
    """Тесты сортировки"""

    fixtures = get_fixtures_list()

    def setUp(self) -> None:
        self.factory = RequestFactory()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.path = reverse("catalog:index")

    # @echo_sql
    def test_sort_by_famous_asc(self) -> None:
        # fix: in deploy
        pass

    # @echo_sql
    def test_sort_by_price_asc(self) -> None:
        sort = "price"

        params = {"sort": sort}
        request = self.factory.get(self.path, params)
        response: TemplateResponse = CatalogListView.as_view()(request)

        result = [offer.price for offer in response.context_data["object_list"]]

        self.check_sort(result)

    # @echo_sql
    def test_sort_by_price_desc(self) -> None:
        sort = "price"
        desc = "on"

        params = {"sort": sort, "desc": desc}
        request = self.factory.get(self.path, params)
        response: TemplateResponse = CatalogListView.as_view()(request)

        result = [offer.price for offer in response.context_data["object_list"]]

        self.check_sort(result, desc=True)

    # @echo_sql
    def test_sort_by_review_asc(self) -> None:
        sort = "review"

        params = {"sort": sort}
        request = self.factory.get(self.path, params)
        response: TemplateResponse = CatalogListView.as_view()(request)

        result = [offer.review_count for offer in response.context_data["object_list"]]

        self.check_sort(result)

    # @echo_sql
    def test_sort_by_review_desc(self) -> None:
        sort = "review"
        desc = "on"

        params = {"sort": sort, "desc": desc}
        request = self.factory.get(self.path, params)
        response: TemplateResponse = CatalogListView.as_view()(request)

        result = [offer.review_count for offer in response.context_data["object_list"]]

        self.check_sort(result, desc=True)

    # @echo_sql
    def test_sort_by_recency_asc(self) -> None:
        sort = "recency"

        params = {"sort": sort}
        request = self.factory.get(self.path, params)
        response: TemplateResponse = CatalogListView.as_view()(request)

        result = [offer.product.manufacturer.modified_at for offer in response.context_data["object_list"]]

        self.check_sort(result)

    # @echo_sql
    def test_sort_by_recency_desc(self) -> None:
        sort = "recency"
        desc = "on"

        params = {"sort": sort, "desc": desc}
        request = self.factory.get(self.path, params)
        response: TemplateResponse = CatalogListView.as_view()(request)

        result = [offer.product.manufacturer.modified_at for offer in response.context_data["object_list"]]

        self.check_sort(result, desc=True)
