from django.core.cache import cache
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from products.models import Product, Category, Detail, Manufacturer
from shops.models import Shop


User = get_user_model()


class ShopViewTestData(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.category = Category.objects.create(name="Тестовая категория2")
        cls.detail = Detail.objects.create(name="тестовая характеристика")
        cls.manufacturer = Manufacturer.objects.create(name="tecтовый производитель")
        cls.product = Product.objects.create(
            name="test product for shop",
            category=cls.category,
            manufacturer=cls.manufacturer,
        )
        cls.product.details.set([cls.detail], through_defaults={"value": "тестовое значение"})

        cls.user = User.objects.create(
            username="test_user_for_shop_test",
            password="QWerty1234",
            email="test_user@mail.com",
        )

        cls.shop = Shop.objects.create(
            user=cls.user,
            name="Test shop 55",
            about="Test description test shop 123124312",
            phone="89006663322",
            email="test-shop-reatailer@mail.com",
            avatar="media/shops/1/avatar/dns.jpg",
        )
        cls.shop.products.set([cls.product], through_defaults={"price": "1235.99", "remains": 0})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cache.clear()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_example_view(self):
        template = "shops/shop_detail.jinja2"
        response = self.client.get(reverse("shops:shop_detail", kwargs={"pk": self.shop.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test-shop-reatailer@mail.com")
        self.assertEqual(response.template_name[0], template)

    def test_shop_products(self):
        response = self.client.get(reverse("shops:shop_products", kwargs={"pk": self.shop.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], "shops/shop_products.jinja2")
        self.assertContains(response, "test product for shop")

    def test_update_shop_information(self):
        response = self.client.get(reverse("shops:shop-update", kwargs={"pk": self.shop.pk}))
        self.assertEqual(response.status_code, 200)

    def test_shop_product_detail(self):
        response = self.client.get(reverse("products:product-detail", kwargs={"pk": self.shop.products.first().pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test product for shop")
