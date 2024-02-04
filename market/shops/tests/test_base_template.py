from django.test import TestCase
from django.shortcuts import render
from django.http.request import HttpRequest


class BaseTemplateTest(TestCase):
    FIXTURES = [
        "fixtures/01-users.json",
        "fixtures/02-groups.json",
        "fixtures/04-shops.json",
        "fixtures/05-category.json",
        "fixtures/06-manufacturer.json",
        "fixtures/07-tags.json",
        "fixtures/08-products.json",
        "fixtures/09-offers.json",
        "fixtures/10-details.json",
        "fixtures/11-productimages.json",
        "fixtures/12-productdetails.json",
        "fixtures/13-reviews.json",
        "fixtures/14-banners.json",
        "fixtures/15-site_settings.json",
        "fixtures/18-limited_offer.json",
    ]

    def test_template_render(self):
        template = "base.jinja2"
        request = HttpRequest()
        # context = {'menu': category_menu()}
        context = {}
        request.session = {}
        response = render(request, template, context=context)
        status = response.status_code
        self.assertEqual(status, 200)
