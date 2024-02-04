import random

from typing import List, Tuple

from django.core.cache import cache
from products.models import Tag


def parse_price(price: str | None = None) -> Tuple[float, float] | None:
    """Функция преобразования цены из строки в кортеж чисел"""

    if not price:
        return

    prices = price.split(";")

    if len(prices) != 2:
        return

    try:
        return float(prices[0]), float(prices[1])

    except ValueError:
        return


def get_famous_tags(count: int = 6) -> List[Tag]:  # fix: сортировка по популярности
    """Функция получения популярных тегов"""
    cache_key = "famous_tags"
    famous_tags = cache.get(cache_key)

    if famous_tags is None:
        famous_tags = list(Tag.objects.order_by("pk"))
        cache.set(cache_key, famous_tags)

    tags = []

    for _ in range(count):
        if not famous_tags:
            break

        tag = random.choice(famous_tags)
        tags.append(tag)
        famous_tags.remove(tag)

    return tags
