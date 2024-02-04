from django.test import TestCase
from django.urls import reverse

from catalog.tests.utils import get_fixtures_list
from shops.models import Offer


class CartViewTest(TestCase):
    fixtures = get_fixtures_list()

    def test_anon_CartView_test(self):
        self.client.logout()
        offer_pk = 3
        offer = Offer.objects.get(pk=offer_pk)
        session = self.client.session
        session["cart"] = {str(offer_pk): "5"}
        session.save()
        response = self.client.get(reverse("cart:user_cart"))
        self.assertContains(response, offer.product.name)
