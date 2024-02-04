from django.template.response import TemplateResponse
from django.test import TestCase, RequestFactory
from django.urls import reverse

from catalog.tests.test_filter import FilterChecker
from catalog.tests.test_sort import SortChecker
from catalog.tests.utils import (
    get_fixtures_list,
    # echo_sql,
)
from catalog.views import CatalogListView


class FilterTest(TestCase, FilterChecker, SortChecker):
    """Тесты фильтра с сортировкой"""

    fixtures = get_fixtures_list()

    def setUp(self) -> None:
        self.factory = RequestFactory()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.path = reverse("catalog:index")

    # @echo_sql
    def test_filter_by_price__sort_by_price_asc(self) -> None:
        start_price = 500_000
        stop_price = 600_000
        price = f"{start_price};{stop_price}"
        sort = "price"

        params = {"price": price, "sort": sort}
        request = self.factory.get(self.path, params)
        response: TemplateResponse = CatalogListView.as_view()(request)

        result = [offer.price for offer in response.context_data["object_list"]]

        self.check_filter_by_price(response, start_price, stop_price)
        self.check_sort(result)

    # @echo_sql
    def test_filter_by_name_price_free_delivery_remains_category__sort_by_review_desc(self) -> None:
        title = "Notebook"
        start_price = 35_000
        stop_price = 40_000
        price = f"{start_price};{stop_price}"
        category_id = 3
        category_name = "Ноутбуки"
        sort = "review"
        desc = "on"

        params = {
            "price": price,
            "title": title,
            "free_delivery": True,
            "remains": True,
            "category_id": category_id,
            "sort": sort,
            "desc": desc,
        }
        request = self.factory.get(self.path, params)
        request.session = {}
        response: TemplateResponse = CatalogListView.as_view()(request)

        result = [offer.review_count for offer in response.context_data["object_list"]]

        self.check_filter_by_name(response, title)
        self.check_filter_by_free_delivery(response)
        self.check_filter_by_remains(response)
        self.check_filter_by_category(response, category_id, category_name)
        self.check_filter_by_price(response, start_price, stop_price)

        self.check_sort(result, desc=True)

    # @echo_sql
    def test_search_with_category__sort_by_recency_desc(self) -> None:
        category_id = 15
        category_name = "Аксессуары"
        search = "Watch"
        sort = "recency"
        desc = "on"

        params = {"category_id": category_id, "search": search, "sort": sort, "desc": desc}
        request = self.factory.get(self.path, params)
        request.session = {}
        response: TemplateResponse = CatalogListView.as_view()(request)

        result = [offer.product.manufacturer.modified_at for offer in response.context_data["object_list"]]

        self.check_filter_by_search(response, search)
        self.check_filter_by_category(response, category_id, category_name)

        self.check_sort(result, desc=True)
