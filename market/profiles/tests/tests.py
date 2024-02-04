from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from products.models import Product, Category, Review, Detail, Manufacturer

from shops.models import Shop, Offer

User = get_user_model()


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


class UserLogoutTest(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        # создает пользователя
        cls.credentials = {"username": "bob_test", "password": "qwerty"}
        cls.user = User.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        self.client.login(**self.credentials)

    def test_logout_user(self):
        response = self.client.get(reverse("profiles:logout"))
        to_reverse = self.client.get(reverse("products:home-page"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("products:home-page"))
        self.assertEqual(to_reverse.status_code, 200)


class UserLoginTest(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        cls.user_login_info = {
            "username": "John-test",
            "email": "jhon@test.com",
            "password": "JohnTest1234",
        }
        cls.profile_info = {
            "phone_number": "89701112233",
            "residence": "London",
            "address": "Bakers streets 148 ap.3",
        }
        cls.user = User.objects.create_user(**cls.user_login_info)

    def setUp(self) -> None:
        self.client.login(
            email=self.user_login_info["email"],
            password=self.user_login_info["password"],
        )

    def test_user_login(self):
        response = self.client.get(reverse("products:home-page"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Content")

    def test_user_login_to_about_user_page(self):
        response = self.client.get(reverse("profiles:about-user"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.template_name)

    def test_user_login_to_change_password_page(self):
        response = self.client.get(reverse("profiles:change-password"))
        self.assertEqual(response.request["PATH_INFO"], "/ru/profiles/change_password/")

    def test_user_login_to_register_page(self):
        response = self.client.get(reverse("profiles:register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registration")
        self.assertContains(response, "Выбрать, если вы хотите стать продавцом на сайте:")


class UserRegisterTest(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        cls.all_info = {
            "username": "John-test",
            "phone": "89701112233",
            "residence": "London",
            "address": "Bakers streets 148 ap.3",
            "retailer_group": True,
        }
        cls.user_login_info = {
            "email": "jhon@test.com",
            "password": "JohnTest1234",
        }

        cls.user = User.objects.create_user(
            username=cls.all_info["username"],
            email=cls.user_login_info["email"],
            password=cls.user_login_info["password"],
            phone=cls.all_info["phone"],
            residence=cls.all_info["residence"],
            address=cls.all_info["address"],
        )

    def setUp(self) -> None:
        self.client.login(**self.user_login_info)

    def test_user_permissions_active(self):
        response = self.client.get(reverse("profiles:home-page"))
        self.assertEqual(response.status_code, 200)

    def test_register_user_sign_in_profile(self):
        response = self.client.get(reverse("profiles:about-user"))
        self.assertEqual(response.status_code, 200)

    def test_register_user_sign_in_change_password(self):
        response = self.client.get(reverse("profiles:change-password"))
        self.assertEqual(response.status_code, 200)

    def test_register_user_sign_in_logout(self):
        response = self.client.get(reverse("profiles:logout"))
        to_home = self.client.get(reverse("products:home-page"))
        url = to_home.wsgi_request.META["PATH_INFO"]
        self.assertEqual(response.url, url)


class UserChangeInformationTest(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        cls.create = {
            "username": "Jhon-test",
            "email": "jhon_test@gmail.com",
            "password": "qwerty1234",
            "phone": "89991112233",
            "residence": "Test residence",
            "address": "California one apple park 1",
            "avatar": "",
        }
        cls.user = User.objects.create_user(**cls.create)

    def setUp(self) -> None:
        self.client.login(email=self.create["email"], password=self.create["password"])

    def test_user_login(self):
        response = self.client.get(reverse("profiles:home-page"))
        self.assertEqual(response.status_code, 200)

    def test_user_get_about_user_page(self):
        response = self.client.get(reverse("profiles:about-user"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, "Страница детальной информации")
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.address)
        self.assertContains(response, self.user.residence)


class UserHaveShopViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Тестовая категория2")
        cls.detail = Detail.objects.create(name="Тестовая характеристика")
        cls.manufacturer = Manufacturer.objects.create(name="tecтовый производитель")
        cls.product = Product.objects.create(
            name="Тестовый продукт", category=cls.category, manufacturer=cls.manufacturer
        )
        cls.product.details.set([cls.detail], through_defaults={"value": "тестовое значение"})
        cls.user = User.objects.create(username="Test_user", email="test@test.com", password="Test123!$")
        cls.review = Review.objects.create(
            user=cls.user, product=cls.product, review_content="Тестовая отзыв продукта"
        )
        cls.shop = Shop.objects.create(user=cls.user, name="тестовый магазин", phone="89991002233")
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=25, remains=0)

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_user_get_shop_page(self):
        response = self.client.get(reverse("shops:shop_detail", kwargs={"pk": self.shop.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "89991002233")

    def test_user_get_shop_update_info(self):
        response = self.client.get(reverse("shops:shop-update", kwargs={"pk": self.shop.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "тестовый магазин")

    def test_user_get_shop_products_page(self):
        response = self.client.get(reverse("shops:shop_products", kwargs={"pk": self.shop.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тестовый продукт")
