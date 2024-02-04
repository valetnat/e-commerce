import time
import json
from threading import Thread, Lock
import requests
from queue import Queue
from django.db import transaction

from orders.services.services import get_order_total_price
from orders.models import Order


class PayThread(Thread):
    """Класс для параллельного запроса в API"""

    def __init__(self, queue: Queue, lock: Lock, url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue_lock = lock
        self.queue: Queue = queue
        self.url = url

    def run(self):
        if not self.queue_lock.locked():
            with self.queue_lock:
                count = 0
                while not self.queue.empty():
                    count += 1
                    order, bank_account, record = self.queue.get()
                    order_price = get_order_total_price(order)
                    params = {"identify_number": order.pk, "cart_number": bank_account, "price": order_price}
                    response = requests.request("POST", url=self.url, data=params)
                    time.sleep(2)
                    with transaction.atomic():
                        if response.status_code == 200:
                            self.set_status_paid_to_order(order=order)
                        self.register_pay_response(record=record, answer_from_api=response.text)
                    return

        else:
            return

    def register_pay_response(self, record, answer_from_api):
        """функция регистрации ответа в БД"""
        record.answer_from_api = json.loads(answer_from_api)
        record.save()

    def set_status_paid_to_order(self, order: Order):
        """функция изменения статуса заказа в БД"""
        order.status = Order.STATUS_PAID
        order.save()

    def set_status_not_paid_to_order(self, order: Order):
        """функция изменения статуса заказа в БД"""
        order.status = Order.STATUS_NOT_PAID
        order.save()
