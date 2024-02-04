from django.core.validators import MaxValueValidator
from django.db import models
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _


class SingletonModel(models.Model):
    """Одноэлементный класс модели"""

    cache_key = "site_settings"

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        """Сохранение экземпляра модели"""
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls) -> "SingletonModel":
        """Получение экземпляра модели"""
        try:
            site_settings = cache.get(cls.cache_key)

            if site_settings:
                return site_settings

            site_settings = cls.objects.get()

            cache.set(key=cls.cache_key, value=site_settings)

        except cls.DoesNotExist:
            site_settings = cls()

        return site_settings


class SortTypeMethod(models.TextChoices):
    """Класс типов сортировки"""

    FAMOUS = "famous", _("По популярности")
    PRICE = "price", _("По цене")
    REVIEW = "review", _("По отзывам")
    RECENCY = "recency", _("По новизне")


class SortDesc(models.TextChoices):
    """Класс состояние сортировки по убыванию"""

    ON = "on", _("Включена")
    OFF = "off", _("Выключена")


class SiteSettings(SingletonModel):
    """Модель настроек сайта"""

    # Prices
    default_price_from = models.DecimalField(
        verbose_name=_("Дефолтная цена от"),
        max_digits=12,
        decimal_places=2,
        default=10.00,
    )
    default_price_to = models.DecimalField(
        verbose_name=_("Дефолтная цена до"),
        max_digits=12,
        decimal_places=2,
        default=1_000.00,
    )

    # Sorting
    default_sort = models.CharField(
        verbose_name=_("Дефолтное поле для сортировки"),
        default="pk",
    )
    default_sort_type = models.CharField(
        verbose_name=_("Дефолтный тип сортировки"),
        choices=SortTypeMethod.choices,
        default=SortTypeMethod.FAMOUS,
    )
    default_sort_desc = models.CharField(
        verbose_name=_("Дефолтная сортировка по убыванию"),
        choices=SortDesc.choices,
        default=SortDesc.ON,
    )

    # Pagination
    paginate_by = models.PositiveSmallIntegerField(
        verbose_name=_("Пагинация"),
        default=8,
    )
    pagination_on_each_side = models.PositiveSmallIntegerField(
        verbose_name=_("Пагинация от центра"),
        default=2,
    )
    pagination_on_ends = models.PositiveSmallIntegerField(
        verbose_name=_("Пагинация по краям"),
        default=1,
    )

    # Cache
    categories_list_cache_timeout = models.PositiveIntegerField(
        verbose_name=_("Время хранения кэша списка категорий, сек."),
        default=60 * 60,
    )

    # Banners
    banner_limit = models.PositiveIntegerField(
        verbose_name=_("Максимальное количество баннеров"),
        validators=[MaxValueValidator(3)],
        default=3,
    )
    offer_limit = models.PositiveIntegerField(
        verbose_name=_("Максимальное количество предложений"),
        validators=[MaxValueValidator(8)],
        default=8,
    )
    foreground_category_limit = models.PositiveIntegerField(
        verbose_name=_("Максимальное количество избранных категорий"),
        validators=[MaxValueValidator(5)],
        default=3,
    )

    class Meta:
        verbose_name_plural = "settings"
        verbose_name = "settings"
