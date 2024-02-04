from decimal import Decimal
from typing import Union

from django.db import models
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from products.models import Product, Category


def promo_image_directory_path(instance: Union["CartPromo", "SetPromo", "ProductPromo"], filename: str) -> str:
    """Функция получения пути для изображений скидок"""
    return "img/promos/{name}/{filename}".format(name=instance.__class__.__name__, filename=filename)


class BasePromo(models.Model):
    """
    Абстрактная модель скидки.
    """

    name = models.CharField(max_length=128, verbose_name=_("наименование скидки"))
    description = models.TextField(max_length=1024, blank=True, verbose_name=_("подробное описание скидки"))
    weight = models.FloatField(
        unique=True, verbose_name=_("вес скидки"), validators=[MinValueValidator(0.01), MaxValueValidator(1.00)]
    )
    preview = models.ImageField(
        null=True, blank=True, upload_to=promo_image_directory_path, verbose_name=_("изображение")
    )
    active_from = models.DateField(verbose_name=_("действует от "))
    active_to = models.DateField(verbose_name=_("действует до "))
    is_active = models.BooleanField(default=False, verbose_name=_("скидка активна"))

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(check=Q(active_from__lt=F("active_to")), name="%(class)s_date_from_lt_date_to"),
        ]


class CartPromo(BasePromo):
    """
    Модель скидка на корзину.
    Скидки могут быть установлены на корзину,
    например на количество товаров в корзине от-до и/или
    на общую стоимость товаров в корзине от-до.
    """

    items_from = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("кол-во товаров в корзине от"))
    items_to = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("кол-во товаров в корзине до"))
    price_from = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("общая стоимость корзины от"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    price_to = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("общая стоимость корзины до"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("размер скидки в рублях"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta(BasePromo.Meta):
        verbose_name = _("скидка на корзину")
        verbose_name_plural = _("скидки на корзину")
        constraints = [
            models.CheckConstraint(check=Q(items_from__lte=F("items_to")), name="items_from_lte_items_to"),
            models.CheckConstraint(check=Q(price_from__lte=F("price_to")), name="price_from_lte_price_to"),
        ]

    def __str__(self) -> str:
        return f"Скидка на корзину (pk={self.pk}, name={self.name!r}, value={self.value!r}руб)"


class SetPromo(BasePromo):
    """
    Модель скиди на наборы.
    Cкидки могут быть установлены на группу товаров,
    если они вместе находятся в корзине.
    Указывается группа товаров 1 и группа товаров 2
    (таким же образом, что и в скидке на товар, то есть раздел и/или конкретный товар).
    """

    sets = models.ManyToManyField("ProductCategorySet", blank=True, verbose_name=_("наборы"))
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("размер скидки в рублях"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta(BasePromo.Meta):
        verbose_name = _("скидка на наборы")
        verbose_name_plural = _("скидки на наборы")

    def __str__(self) -> str:
        return f"Cкидка на набор (pk={self.pk}, name={self.name!r}, value={self.value!r}руб)"


class ProductPromo(BasePromo):
    """
    Модель скидки на товар.
    Cкидки могут быть установлены на указанный список товаров и/или
    на указанные категории товаров.
    """

    products = models.ManyToManyField(
        Product, blank=True, related_name="products_prodoctpromos", verbose_name=_("товары")
    )
    categories = models.ManyToManyField(
        Category, blank=True, related_name="categories_prodoctpromos", verbose_name=_("категории")
    )
    value = models.IntegerField(
        verbose_name=_("размер скидки в процентах"), validators=[MinValueValidator(1), MaxValueValidator(99)]
    )

    class Meta(BasePromo.Meta):
        verbose_name = _("скидка на продукт(ы) и/или категорию(ии)")
        verbose_name_plural = _("скидки на продукт(ы) и/или категорию(ии)")

    def __str__(self) -> str:
        return f"Cкидка на продукт(ы) и/или категорию(ии)(pk={self.pk}, name={self.name!r}, value={self.value!r}%)"


class ProductCategorySet(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("наименование набора"))
    products = models.ManyToManyField(Product, blank=True, verbose_name=_("набор товаров"))
    categories = models.ManyToManyField(Category, blank=True, verbose_name=_("набор категорий"))

    class Meta:
        verbose_name = _("набор")
        verbose_name_plural = _("наборы")

    def __str__(self) -> str:
        return f"Набор (pk={self.pk}, name={self.name!r}%)"
