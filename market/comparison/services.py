from typing import Dict, Any, List
from django.conf import settings
from products.models import Product, ProductDetail
from django.http import HttpRequest
from django.utils import timezone


class ComparisonService:
    def __init__(self, request: HttpRequest) -> None:
        """
        Инициализирование сравнения.
        """
        self.session = request.session
        comparison = self.session.get(settings.COMPARISON_SESSION_ID)

        if not comparison:
            comparison = self.session[settings.COMPARISON_SESSION_ID] = {}

        self.comparison = comparison

    def add(self, product: Product) -> bool:
        """
        Добавление товара в список сравнения.
        """
        product_id = str(product.id)

        if product_id not in self.comparison:
            self.comparison[product_id] = {
                "detail": {},
                "name": product.name,
                "category": product.category.name,
                "preview": (product.preview.url if product.preview else ""),
                "created_at": str(timezone.now()),
            }

            productdetails = ProductDetail.objects.select_related("detail", "product").filter(product=product_id)

            for productdetail in productdetails:
                self.comparison[product_id]["detail"][productdetail.detail.name] = productdetail.value

            self.save()
            return True

        else:
            return False

    def save(self) -> None:
        """
        Сохранение измененной сессии.
        """
        self.session.modified = True

    def remove(self, product: Product) -> None:
        """
        Удаление товара из списка сравнения.
        """
        product_id = str(product.id)

        if product_id in self.comparison:
            del self.comparison[product_id]

        self.save()

    def clear(self) -> None:
        """
        Очистка всего списка товаров для сравнения.
        """
        del self.session[settings.COMPARISON_SESSION_ID]
        self.save()

    def get_valid_products_list(self, max_products: int = settings.COMPARISON_MAX_PRODUCTS) -> Dict[str, Any]:
        """
        Валидация списка по макс. кол-ву товаров.
        :param max_products: макс. кол-во товаров для сравнения
        :return:
            valid_list - список доступных товаров
        """
        valid_list = dict()
        count = 1

        for k, v in self.comparison.items():
            if count > max_products:
                break
            count += 1
            valid_list[k] = v
        return valid_list

    @classmethod
    def get_common_diff_details(cls, details_to_compare: List[str], valid_list: Dict[str, Any]):
        """
        Получение списка общих и отличающихся характеристик товара
        :param details_to_compare: список уникальных характеристик
        :param valid_list: список доступных товаров
        :return:
            common_attribute - спискок общих характеристик товара
            different_attribute - спискок отличающихся характеристик товара
        """
        common_attribute = list()
        different_attribute = list()
        for detail_to_compare in details_to_compare:
            if all(details["detail"].get(detail_to_compare, None) is not None for details in valid_list.values()):
                common_attribute.append(detail_to_compare)
            else:
                different_attribute.append(detail_to_compare)

        return common_attribute, different_attribute

    @classmethod
    def compare(cls, details_to_compare: List[str], valid_list: Dict[str, Any]) -> Dict[str, Any]:
        """
        Сравнения характеристик товара.
        Если характеристика товара отсутсутвует, добавляет ее со значением 'x'.
        :param details_to_compare: список уникальных характеристик
        :param valid_list: список доступных товаров
        :return:
            valid_list - список товаров с полным набором харктеристик
        """
        for product_id, product_data in valid_list.items():
            details = product_data.get("detail", {})

            for detail_to_compare in details_to_compare:
                processor_line = details.get(detail_to_compare)

                if processor_line is None:
                    details[detail_to_compare] = "x"
        return valid_list

    @classmethod
    def get_all_unique_details(
        cls, valid_list: Dict[str, Any], max_products: int = settings.COMPARISON_MAX_PRODUCTS
    ) -> List[str]:
        """
        Получение уникальных характеристик доступных к сравнению товаров
        :param max_products: максимально число товаров для сравнения
        :param valid_list:  список доступных товаров
        :return:
        """
        return sorted(
            (
                str(productdetail.detail.name)
                for productdetail in ProductDetail.objects.select_related("detail", "product")
                .filter(product_id__in=list(valid_list.keys())[:max_products])
                .distinct("detail__name")
            )
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__ }"

    def __len__(self) -> int:
        return len(self.comparison.keys())
