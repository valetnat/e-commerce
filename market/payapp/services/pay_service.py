from queue import Queue
from threading import Lock
from django.conf import settings
from django.db import transaction

from payapp.services.pay_processor import PayThread
from orders.models import Order
from payapp.forms import BancAccountForm
from payapp.models import OrderPayStatus


def pay_order(order: Order, bank_account: int, host_name: str) -> None:
    """Постановка в очередь и обработка запроса в API"""
    pay_queue: Queue = settings.PAY_QUEUE
    lock: Lock = settings.PAY_QUEUE_LOCK
    pay_url = settings.PAY_URL
    url = "http://" + host_name + pay_url

    record = OrderPayStatus(order=order)
    order.status = Order.STATUS_NOT_PAID
    with transaction.atomic():
        order.save()
        record.save()
    task = (order, bank_account, record)
    pay_queue.put(task, block=True)
    PayThread(pay_queue, lock, url).start()


def invalid_form(order: Order, form: BancAccountForm) -> None:
    """Обработка невалидного счета"""
    order.status = Order.STATUS_NOT_PAID
    record = OrderPayStatus(order=order, answer_from_api={"error": form.errors})
    with transaction.atomic():
        record.save()
        order.save()
