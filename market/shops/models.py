from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _

from profiles.models import User


def shop_avatar_path(instance: "User", filename):
    return "shops/{pk}/avatar/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Shop(models.Model):
    """Магазин"""

    # Магазин связан с пользователем
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True, related_name="shops")
    name = models.CharField(max_length=512, verbose_name=_("название"))
    about = models.TextField(
        verbose_name=_("Описание магазина"),
        help_text=_("Введите краткое описание магазина."),
        default=_("Описание магазина"),
    )
    phone = models.CharField(
        max_length=11,
        verbose_name=_("Телефон магазина"),
        help_text=_("Контактный телефон магазина."),
        default="89001112233",
    )
    email = models.EmailField(
        verbose_name=_("Емаил магазина"),
        help_text=_("Контактный емаил магазина."),
        null=True,
    )
    avatar = models.ImageField(verbose_name=_("Аватар"), upload_to=shop_avatar_path, null=True)
    products = models.ManyToManyField(
        "products.Product",
        through="Offer",
        related_name="shops",
        related_query_name="shop",
        verbose_name=_("товары в магазине"),
    )

    class Meta:
        verbose_name = _("магазин")
        verbose_name_plural = _("магазины")

    def __str__(self) -> str:
        return f"Продавец (pk={self.pk}, name={self.name!r})"


class PaymentMethod(models.TextChoices):
    """Модель для выбора способа оплаты"""

    CARD = "CARD", _("Банковской картой")
    CASH = "CASH", _("Наличными")


class DeliveryMethod(models.TextChoices):
    """Модель для выбора способа доставки"""

    FREE = "FREE", _("Бесплатная доставка")
    REGULAR = "REGULAR", _("Обычная доставка")
    EXPRESS = "EXPRESS", _("Экспресс доставка")


class Offer(models.Model):
    """Предложение магазина"""

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="offers")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("цена"), validators=[MinValueValidator(Decimal("0.01"))]
    )
    remains = models.PositiveIntegerField(verbose_name=_("остаток"))
    payment_method = models.CharField(
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD,
        verbose_name=_("способ оплаты"),
        max_length=128,
    )
    delivery_method = models.CharField(
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.REGULAR,
        verbose_name=_("способ доставки"),
        max_length=128,
    )

    class Meta:
        verbose_name = _("предложение магазина")
        verbose_name_plural = _("предложения магазина")

    def __str__(self) -> str:
        return f"Предложение (pk={self.pk}, shop={self.shop.name!r}), product={self.product.name!r}"
