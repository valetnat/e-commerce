from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Category


@receiver(post_delete, sender=Category, dispatch_uid="category_post_deleted")
def object_post_delete_handler(sender, **kwargs):
    """Функция валидации кеша при DELETE запросе модели Категории"""

    cache.delete("categories_data_export")


@receiver(post_save, sender=Category, dispatch_uid="category_posts_updated")
def object_post_save_handler(sender, **kwargs):
    """Функция валидации кеша при SAVE, UPDATE запросах модели Категории"""

    cache.delete("categories_data_export")
