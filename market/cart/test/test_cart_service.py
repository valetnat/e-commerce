from django.test import TestCase

from django.test.client import RequestFactory

from django.conf import settings
from django.contrib import auth
from django.utils.functional import SimpleLazyObject
from importlib import import_module

from catalog.tests.utils import get_fixtures_list
from shops.models import Offer
from cart.services import cart_service


def get_user(request):
    if not hasattr(request, "_cached_user"):
        request._cached_user = auth.get_user(request)
    return request._cached_user


def middleware(request):
    engine = import_module(settings.SESSION_ENGINE)
    SessionStore = engine.SessionStore
    session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
    request.session = SessionStore(session_key)
    request.user = SimpleLazyObject(lambda: get_user(request))
    return request


class AnonimCartServiceTest(TestCase):
    fixtures = get_fixtures_list()

    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = middleware(self.factory.request())

    def test_get_AnonimCart(self):
        cart = cart_service.get_cart_service(self.request)
        self.assertIsInstance(cart, cart_service.AnonimCartService)
        self.assertEqual(self.request.session["cart_size"], str(0))
        self.assertEqual(self.request.session["cart_price"], "0.00")

    def test_add_AnonimCart(self):
        cart = cart_service.get_cart_service(self.request)
        offer = Offer.objects.get(pk=2)
        cart.add_to_cart(offer.pk)
        session_cart = self.request.session["cart"]
        expected_amount = 1
        expected_cart = {str(offer.pk): str(expected_amount)}
        price = Offer.objects.get(pk=offer.pk).price
        self.assertDictEqual(session_cart, expected_cart)
        self.assertEqual(self.request.session["cart_size"], str(expected_amount))
        self.assertEqual(self.request.session["cart_price"], str(price))

    def test_re_add_AnonimCart(self):
        cart = cart_service.get_cart_service(self.request)
        offer = Offer.objects.get(pk=2)
        cart.add_to_cart(offer.pk, 1)
        amount = "5"
        cart.add_to_cart(offer.pk, amount)
        session_cart = self.request.session["cart"]
        expected_amount = 6
        expected_cart = {str(offer.pk): str(expected_amount)}
        price = offer.price * expected_amount
        self.assertDictEqual(session_cart, expected_cart)
        self.assertEqual(self.request.session["cart_size"], str(expected_amount))
        self.assertEqual(self.request.session["cart_price"], str(price))

    def test_add_one_more_offer_AnonimCart(self):
        cart = cart_service.get_cart_service(self.request)
        offer_list = [Offer.objects.get(pk=i) for i in range(1, 15, 5)]
        for offer in offer_list:
            cart.add_to_cart(offer.pk)
        session_cart = self.request.session["cart"]
        expected_cart = {str(offer.pk): str(1) for offer in offer_list}
        expected_amount = len(offer_list)
        price = sum([offer.price for offer in offer_list])
        self.assertDictEqual(session_cart, expected_cart)
        self.assertEqual(self.request.session["cart_size"], str(expected_amount))
        self.assertEqual(self.request.session["cart_price"], str(price))

    def test_delete_offer_AnonimCart(self):
        self.request.session["cart"] = cart = {"10": "5", "1": "3"}
        offer_dict = Offer.objects.filter(pk__in=[int(key) for key in cart.keys()]).in_bulk(field_name="id")
        self.request.session["cart_size"] = "8"
        price = sum([offer_dict[pk].price * int(cart[str(pk)]) for pk in offer_dict.keys()])
        self.request.session["cart_price"] = str(price)
        cart = cart_service.get_cart_service(self.request)
        cart.remove_from_cart(10)
        session_cart = self.request.session["cart"]
        expected_cart = {"1": "3"}
        expected_amount = "3"
        expected_price = Offer.objects.get(pk=1).price * 3
        self.assertDictEqual(session_cart, expected_cart)
        self.assertEqual(self.request.session["cart_size"], str(expected_amount))
        self.assertEqual(self.request.session["cart_price"], str(expected_price))

    def test_clear_AnonimCart(self):
        self.request.session["cart"] = {"10": "5", "1": "3"}
        cart = cart_service.get_cart_service(self.request)
        cart.clear()
        session_cart = self.request.session["cart"]
        expected_cart = {}
        self.assertDictEqual(session_cart, expected_cart)
        self.assertEqual(self.request.session["cart_size"], str(0))
        self.assertEqual(self.request.session["cart_price"], "0.00")

    def test_session_cart_size(self):
        cart = cart_service.get_cart_service(self.request)
        cart.add_to_cart(5, 5)
        cart.add_to_cart(3, 1)
        cart_size = self.request.session["cart_size"]
        expected_cart_size = "6"
        self.assertEqual(cart_size, expected_cart_size)

    def test_clear_cart_size(self):
        self.request.session["cart"] = {"10": "5", "1": "3"}
        cart = cart_service.get_cart_service(self.request)
        cart.clear()
        cart_size = self.request.session["cart_size"]
        expected_cart_size = "0"
        self.assertEqual(cart_size, expected_cart_size)

    def test_update_AnonimCart(self):
        self.request.session["cart"] = {"10": "5", "1": "3", "15": "6"}
        service = cart_service.get_cart_service(self.request)
        service.update_cart({10: 1, 15: 1, 1: 3})
        new_cart = self.request.session["cart"]
        expected_cart = {"10": "1", "15": "1", "1": "3"}
        self.assertDictEqual(new_cart, expected_cart)

    def test_get_price_AnonimCart(self):
        session_cart = self.request.session["cart"] = {"10": "5", "1": "3", "15": "6"}
        offer_dict = Offer.objects.filter(pk__in=[int(key) for key in session_cart.keys()]).in_bulk(field_name="id")
        expected_price = 0
        for pk in offer_dict.keys():
            expected_price += offer_dict[pk].price * int(session_cart[str(pk)])
        service = cart_service.get_cart_service(self.request)
        price = service.get_upd_price()
        self.assertEqual(price, str(expected_price))
