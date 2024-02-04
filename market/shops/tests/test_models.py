from django.core.cache import cache
from django.test import TestCase
from shops.models import Shop, Offer
from products.models import Product, Detail, Category, Manufacturer
from django.contrib.auth import get_user_model

User = get_user_model()


class ShopModelTest(TestCase):
    """Класс тестов модели Магазин"""

    @classmethod
    def setUpTestData(cls):
        cls.detail = Detail.objects.create(name="тестовая характеристика")
        cls.category = Category.objects.create(name="тестовая категория")
        cls.manufacturer = Manufacturer.objects.create(name="tecтовый производитель")
        cls.product = Product.objects.create(
            name="тестовый продукт", category=cls.category, manufacturer=cls.manufacturer
        )
        cls.product.details.set([cls.detail])
        cls.user = User.objects.create(
            username="test_user_for_shop_test",
            password="QWerty1234",
            email="test_user@mail.com",
        )
        cls.shop = Shop.objects.create(user=cls.user, name="тестовый магазин")
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=25, remains=12)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        ShopModelTest.detail.delete()
        ShopModelTest.product.delete()
        ShopModelTest.shop.delete()
        ShopModelTest.offer.delete()
        ShopModelTest.category.delete()
        ShopModelTest.manufacturer.delete()
        ShopModelTest.user.delete()

    def test_verbose_name(self):
        shop = ShopModelTest.shop
        field_verboses = {
            "name": "название",
            "products": "товары в магазине",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(shop._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        shop = ShopModelTest.shop
        max_length = shop._meta.get_field("name").max_length
        self.assertEqual(max_length, 512)


class OfferModelTest(TestCase):
    """Класс тестов модели Предложение магазина"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="тестовая категория")
        cls.manufacturer = Manufacturer.objects.create(name="tecтовый производитель")
        cls.product = Product.objects.create(
            name="тестовый продукт", category=cls.category, manufacturer=cls.manufacturer
        )
        cls.user = User.objects.create(
            username="test_user_for_shop_test",
            password="QWerty1234",
            email="test_user@mail.com",
        )
        cls.shop = Shop.objects.create(user=cls.user, name="тестовый магазин")
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=35, remains=2)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        OfferModelTest.product.delete()
        OfferModelTest.shop.delete()
        OfferModelTest.offer.delete()
        OfferModelTest.category.delete()
        OfferModelTest.manufacturer.delete()
        OfferModelTest.user.delete()

    def test_verbose_name(self):
        offer = OfferModelTest.offer
        field_verboses = {
            "price": "цена",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(offer._meta.get_field(field).verbose_name, expected_value)

    def test_price_max_digits(self):
        offer = OfferModelTest.offer
        max_digits = offer._meta.get_field("price").max_digits
        self.assertEqual(max_digits, 10)

    def test_price_decimal_places(self):
        offer = OfferModelTest.offer
        decimal_places = offer._meta.get_field("price").decimal_places
        self.assertEqual(decimal_places, 2)

    def test_price(self):
        pass

    def test_product_fields_name(self):
        attr_names = dir(self.offer)
        variable_name_in_template = (
            "shop",
            "product",
            "price",
            "get_delivery_method_display",
            "get_payment_method_display",
        )
        for name in variable_name_in_template:
            self.assertIn(name, attr_names)


class ShopDataModelTest(TestCase):
    """Класс тестов модели Магазин"""

    @classmethod
    def setUpTestData(cls):
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

    def test_verbose_name(self):
        shop = ShopDataModelTest.shop
        field_verboses = {
            "name": "название",
            "about": "Описание магазина",
            "phone": "Телефон магазина",
            "email": "Емаил магазина",
            "avatar": "Аватар",
            "products": "товары в магазине",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(shop._meta.get_field(field).verbose_name, expected_value)

    def test_check_the_database_for_compliance(self):
        self.assertEqual(self.shop.name, "Test shop 55")
        self.assertEqual(self.shop.email, "test-shop-reatailer@mail.com")
        self.assertEqual(self.shop.phone, "89006663322")
        self.assertEqual(self.shop.avatar, "media/shops/1/avatar/dns.jpg")
        self.assertEqual(self.shop.user.username, "test_user_for_shop_test")
        self.assertEqual(self.shop.user.email, "test_user@mail.com")
