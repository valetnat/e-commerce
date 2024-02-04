from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderPayStatus(models.Model):
    """Модель для хранения ответа от сервера оплаты"""

    order = models.ForeignKey(
        to="orders.Order", related_name="payrecords", verbose_name=_("заказ"), on_delete=models.CASCADE
    )
    answer_from_api = models.JSONField(verbose_name=_("ответ сервиса оплаты"), null=True)
    created_at = models.DateTimeField(verbose_name=_("дата выполнения"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("история оплаты заказа")
        verbose_name_plural = _("истории оплаты заказа")
