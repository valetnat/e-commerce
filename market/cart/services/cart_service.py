from typing import Union

from django.http import HttpRequest
from django.conf import settings
from shops.models import Offer


class AnonimServiceException(Exception):
    pass


class AnonimCartService:
    """Сервис корзины для анонимного пользователя. Все записи, цена и кол-во товара хранятся в сессии"""

    def __init__(self, request: HttpRequest):
        self.session = request.session
        session_cart = self.session.get(settings.CART_SESSION_KEY)
        if not session_cart:
            session_cart = self.session[settings.CART_SESSION_KEY] = {}
        self.session_cart = session_cart

        session_cart_length = self.session.get(settings.CART_SIZE_SESSION_KEY)
        if not session_cart_length:
            self.session[settings.CART_SIZE_SESSION_KEY] = "0"
        self.session_cart_length = self.session[settings.CART_SIZE_SESSION_KEY]

        session_cart_price = self.session.get(settings.CART_PRICE_SESSION_KEY)
        if not session_cart_price:
            self.session[settings.CART_PRICE_SESSION_KEY] = "0.00"
        self.session_cart_price = self.session[settings.CART_PRICE_SESSION_KEY]

    def _save_cart(self):
        self.session.modified = True

    def _change_session_cart_length(self, amount: Union[str, int], add: bool = True):
        cart_size = int(self.session[settings.CART_SIZE_SESSION_KEY])
        if add:
            self.session[settings.CART_SIZE_SESSION_KEY] = str(cart_size + int(amount))
        else:
            self.session[settings.CART_SIZE_SESSION_KEY] = str(cart_size - int(amount))

    def _change_session_cart_price(self, money: Union[str, float], add: bool = True):
        cart_price = float(self.session[settings.CART_PRICE_SESSION_KEY])
        if add:
            self.session[settings.CART_PRICE_SESSION_KEY] = "{:.2f}".format(cart_price + float(money))
        else:
            self.session[settings.CART_PRICE_SESSION_KEY] = "{:.2f}".format(cart_price - float(money))

    def get_cart_as_dict(self):
        """Получает список из UserOfferCart без атрибута user на основании сессии"""
        if not self.session_cart:
            return {}
        return {int(k): int(v) for k, v in self.session_cart.items()}

    def remove_from_cart(self, offer_id: int):
        """
        Удаляет одну запись(Offer) активной корзины
        :param offer_id: Offer.pk - ID модели Offer
        :return:
        """
        try:
            current_amount = self.session_cart.pop(str(offer_id))

            self._change_session_cart_length(amount=current_amount, add=False)

            offer = Offer.objects.get(pk=offer_id)
            self._change_session_cart_price(money=offer.price * int(current_amount), add=False)
            self._save_cart()
        except KeyError:
            return

    def add_to_cart(self, offer_id: int, amount: Union[int, str] = 1):
        """
        Добавляет к существующей корзине запись, если такая запись уже существует добавляет количество.
        :param offer_id:
        :param amount:
        :return:
        """
        current_amount = int(self.session_cart.get(str(offer_id), "0"))
        self.session_cart[str(offer_id)] = str(current_amount + int(amount))
        self._change_session_cart_length(amount=amount)
        offer = Offer.objects.get(pk=offer_id)
        self._change_session_cart_price(money=offer.price * int(amount))
        self._save_cart()

    def change_amount(self, offer_id: int, amount: int):
        """
        Изменяет количество в существующей записи корзине
        :param offer_id:
        :param amount:
        :return:
        """
        current_amount = self.session_cart.get(str(offer_id))
        if not current_amount:
            raise AnonimServiceException("Такого предложения не найдено в корзине")
        offer = Offer.objects.get(pk=offer_id)
        current_amount = int(current_amount)
        self._change_session_cart_length(amount=(amount - current_amount))
        self._change_session_cart_price(money=offer.price * (amount - current_amount))

        self.session_cart[str(offer_id)] = str(amount)
        self._save_cart()

    def update_cart(self, data: dict):
        """
        Изменяет анонимную корзину согласно переданному словарю. Данные предыдущей корзины удаляться.
        :param data:  is dict where key = offer_id; value = amount например data = {Offer.pk: amount, ... }
        :return:
        """
        new_data = {}
        cart_size = 0
        for k, v in data.items():
            if v > 0:
                new_data[str(k)] = str(v)
                cart_size += v
        self.session_cart = self.session[settings.CART_SESSION_KEY] = new_data
        self.contains_remaining_offers()
        self.session[settings.CART_SIZE_SESSION_KEY] = str(cart_size)
        self._update_price()
        self._save_cart()

    def contains_remaining_offers(self):
        self.session_cart = self.session[settings.CART_SESSION_KEY]
        for offer_pk, values in self.session_cart.items():
            offer = Offer.objects.get(pk=offer_pk)
            if int(values) > offer.remains:
                self.session_cart[f"{offer_pk}"] = offer.remains

    def _update_price(self):
        sum_price = 0
        offers_dict = Offer.objects.filter(pk__in=self.session_cart.keys()).only("price").in_bulk(field_name="id")
        for str_offer_id, str_amount in self.session_cart.items():
            price = offers_dict[int(str_offer_id)].price
            sum_price += price * int(str_amount)
        self.session[settings.CART_PRICE_SESSION_KEY] = str(sum_price)
        self._save_cart()

    def get_upd_price(self):
        """Обновляет цену для всей корзины на основе данных из БД и возвращает это значение"""
        self._update_price()
        return self.session[settings.CART_PRICE_SESSION_KEY]

    def get_upd_length(self):
        """Обновляет кол-во товара для всей корзины на основе данных в сессии и возвращает это значение"""
        length = 0
        for amount in self.session_cart.values():
            length += int(amount)
        self.session[settings.CART_SIZE_SESSION_KEY] = str(length)
        self._save_cart()
        return length

    def get_offers_len(self) -> int:
        """Возвращает количество записей в корзине сессии"""
        length = len(self.session_cart)
        return length

    def __len__(self):
        """Возвращает значение равное кол-ву товара хранимое в сессии session['cart_size"]"""
        return int(self.session[settings.CART_SIZE_SESSION_KEY])

    def clear(self):
        """Удаляет и обнуляет анонимную корзину"""
        self.session_cart.clear()
        self._save_cart()
        self.session[settings.CART_SIZE_SESSION_KEY] = "0"
        self.session[settings.CART_PRICE_SESSION_KEY] = "0.00"

    def append_cart_to_history(self):
        """Не применимо к анонимной корзине. функция для сохранения записей корзины в истории"""
        raise AnonimServiceException(
            "Такой метод недопустим для анонимной корзины",
        )


def get_cart_service(request: HttpRequest) -> AnonimCartService:
    """Функция для получения сервиса для работы с корзиной. Если пользователь анонимный,
    то возвращает сервис для Анонимной корзины работающий на сессиях. Иначе возвращает сервис для корзины пользователя,
    работающий через БД.
    """
    return AnonimCartService(request)


def login_cart(request: HttpRequest) -> None:
    """Обновление пользовательской корзины при входе пользователя, все записи анонимной корзины мигрируют в
    пользовательскую корзину"""
    return
