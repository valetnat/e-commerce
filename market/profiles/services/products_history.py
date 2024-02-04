import datetime
from django.utils import timezone

from profiles.models import User, UserProductHistory
from products.models import Product

HISTORY_SIZE = 9


def is_product_in_history(user: User, product: Product):
    """Есть ли товар в истории просмотра пользователя"""
    return UserProductHistory.objects.filter(user=user, product=product).exists()


def get_history_length(user: User):
    """Возвращает количество записей в истории"""
    return UserProductHistory.objects.filter(user=user).count()


def get_latest_product(user: User):
    """Возвращает последний товар в истории"""
    latest_product = user.product_in_history.order_by("userproducthistory").first()
    return latest_product


def get_products_in_user_history(user: User, number: int = HISTORY_SIZE):
    """Получение отсортированного по времени списка товаров из истории просмотров
    Пользователь должен быть аутентифицирован."""
    history = user.product_in_history.order_by("userproducthistory").all()[:number]
    return history


def validate_user_history(user: User):
    history = (
        UserProductHistory.objects.filter(user=user).order_by("-time")[: HISTORY_SIZE - 1].values_list("id", flat=True)
    )
    UserProductHistory.objects.exclude(pk__in=list(history)).delete()


def make_record_in_history(user: User, product: Product, recurse=False):
    if not recurse:
        latest_product = get_latest_product(user)
        if latest_product == product:
            return
        if is_product_in_history(user, product):
            UserProductHistory.objects.filter(user=user, product=product).update(
                time=datetime.datetime.now(tz=timezone.get_current_timezone())
            )
            return
    history_length = get_history_length(user)
    if history_length == HISTORY_SIZE:
        record = UserProductHistory.objects.filter(user=user).order_by("-time").last()
        record.product = product
        record.time = datetime.datetime.now(tz=timezone.get_current_timezone())
        record.save()
        return
    if history_length < HISTORY_SIZE:
        UserProductHistory(user=user, product=product).save()
        return
    if history_length > HISTORY_SIZE:
        validate_user_history(user)
        make_record_in_history(user, product, True)
