from django.core.paginator import Paginator, Page
from django.http import HttpRequest
from django.db.models import QuerySet

from products.models import Review, Product


class ReviewServices:
    """Сервис для работы с отзывами"""

    def __init__(self, request: HttpRequest, product: Product) -> None:
        self.request = request
        self.product = product

    def add_review(self, text: str) -> None:
        """
        Добавление отзыва к товару
        :param text: текст отзыва о товаре
        :return: None
        """
        Review.objects.create(
            user=self.request.user,
            product=self.product,
            review_content=text,
            is_published=True,
        )

    def get_reviews(self) -> QuerySet:
        """
        Получение отзывов о товаре
        :return: список отзывов о товаре
        """
        reviews = self.product.review_set.filter(is_published=True, archived=False).order_by("-created_at").all()
        return reviews

    def get_reviews_num(self) -> int:
        """
        Получение количества отзывов о товаре
        :return: reviews_num: int - количество отзывов
        """
        reviews_num = (
            Review.objects.select_related("parent", "product")
            .filter(product=self.product, is_published=True, archived=False)
            .count()
        )
        return reviews_num

    def listing(self, reviews: QuerySet) -> Page:
        """
        Возвращает объект пагинации для работы пагинации отзывов о товарах
        :param reviews: список отзывов о товаре
        :return: объект пагинации

        doc: https://docs.djangoproject.com/en/4.2/topics/pagination/#using-paginator-in-a-view-function
        """
        paginator = Paginator(reviews, 3)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return page_obj
