from django.db import models
from django.utils.translation import gettext_lazy as _

from profiles.models import User
from django.db.models import Q


class DeliveryType(models.TextChoices):
    """Модель выбора способа доставки."""

    USUALLY = "usually", _("обычная доставка")
    EXPRESS = "express", _("экспресс доставка")


class PaymentType(models.TextChoices):
    """Модель выбора способа оплаты."""

    CARD = "card", _("онлайн картой")
    RANDOM = "random", _("Онлайн со случайного чужого счета")


class Order(models.Model):
    """Класс модели таблицы заказов"""

    STATUS_CREATED = _("создан")
    STATUS_OK = _("выполнен")
    STATUS_DELIVERED = _("доставляется")
    STATUS_PAID = _("оплачен")
    STATUS_NOT_PAID = _("не оплачен")

    STATUS_CHOICES = [
        (
            "Success",
            (
                (STATUS_CREATED, "создан"),
                (STATUS_OK, "выполнен"),
                (STATUS_DELIVERED, "доставляется"),
                (STATUS_PAID, "оплачен"),
            ),
        ),
        (STATUS_NOT_PAID, "не оплачен"),
    ]

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("дата создания заказа"),
    )
    city = models.CharField(
        max_length=50,
        verbose_name=_("Город доставки"),
        blank=True,
    )
    address = models.CharField(max_length=260, verbose_name=_("адрес доставки"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    delivery_type = models.CharField(
        max_length=50,
        choices=DeliveryType.choices,
        default=DeliveryType.USUALLY,
        verbose_name=_("метод доставки"),
    )
    payment_type = models.CharField(
        max_length=50,
        choices=PaymentType.choices,
        # blank=False,
        default=PaymentType.CARD,
        verbose_name=_("способ оплаты"),
    )
    order_number = models.PositiveIntegerField(default=1, verbose_name=_("номер заказа"))
    # fmt: off
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name="status"
    )
    # fmt: on
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("общая стоимость"),
    )
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Размер скидки"), default=0.00
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("заказ")
        verbose_name_plural = _("заказы")
        constraints = [models.CheckConstraint(check=Q(total_price__gte=1.00), name="total_price_lte_1.00")]

    def __str__(self):
        return f"Заказ#{self.pk}:{self.user.username}"

    def get_order_number(self, user: User):
        all_examples = self.objects.filter(user=user).first().order_number
        self.order_number = all_examples + 1
        return self.order_number


class OrderDetail(models.Model):
    """
    Класс модели деталей заказа
    (предложения и продукты загружаемые из корзины)
    """

    offer = models.ForeignKey(
        to="shops.Offer",
        on_delete=models.CASCADE,
        verbose_name=_("Предложение"),
        help_text=_("Выбрать желаемый товар по специальной цене от магазина"),
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Количество товара"))
    user_order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="details", verbose_name=_("Номер заказа пользователя")
    )

    class Meta:
        verbose_name = _("заказ пользователя")
        verbose_name_plural = _("заказы пользователя")

    def __str__(self):
        return f"Товар {self.offer.product.name}"

    def get_coast(self):
        return self.offer.price * self.quantity
