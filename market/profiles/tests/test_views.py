from django.test import TestCase
from profiles.models import User
from products.models import Product
from django.urls import reverse
from profiles.models import UserProductHistory

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


class UserHistoryViewTest(TestCase):
    """Класс тестов для записей в истории посещения пользователя"""

    fixtures = FIXTURES

    def setUp(self) -> None:
        self.user = User.objects.all().first()
        self.client.force_login(self.user)

    def test_permissions(self):
        self.client.logout()
        response = self.client.get(reverse("profiles:browsing_history"))
        status = response.status_code
        self.assertEqual(status, 302)

    def test_status_login_user(self):
        response = self.client.get(reverse("profiles:browsing_history"))
        status = response.status_code
        self.assertEqual(status, 200)

    def test_history(self):
        products = []
        for pk in range(1, 8):
            UserProductHistory(user=self.user, product_id=pk).save()
            product = Product.objects.get(pk=pk)
            products.append(product)
        response = self.client.get(reverse("profiles:browsing_history"))
        self.assertContains(response, products[2].name)

    def test_last_record_history(self):
        products = []
        history_length = 9
        for pk in range(1, history_length + 1 + 2):
            UserProductHistory(user=self.user, product_id=pk).save()
            product = Product.objects.get(pk=pk)
            products.append(product)
        response = self.client.get(reverse("profiles:browsing_history"))
        self.assertContains(response, products[-1].name)


class AboutUserViewTest(TestCase):
    fixtures = FIXTURES

    def setUp(self) -> None:
        self.user = User.objects.all().first()
        self.client.force_login(self.user)

    def test_history(self):
        products = []
        for pk in range(1, 4):
            UserProductHistory(user=self.user, product_id=pk).save()
            product = Product.objects.get(pk=pk)
            products.append(product)
        response = self.client.get(reverse("profiles:about-user"))
        self.assertContains(response, products[2].name)

    def test_last_product_in_history(self):
        products = []
        for pk in range(1, 8):
            UserProductHistory(user=self.user, product_id=pk).save()
            product = Product.objects.get(pk=pk)
            products.append(product)
        response = self.client.get(reverse("profiles:about-user"))
        self.assertContains(response, products[-1].name)

    def test_null_history(self):
        response = self.client.get(reverse("profiles:about-user"))
        self.assertNotContains(response, "Вы смотрели")

    def test_some_history(self):
        self.client.get(reverse("products:product-detail", kwargs={"pk": 1}))
        response = self.client.get(reverse("profiles:about-user"))
        self.assertContains(response, "Вы смотрели")


class PasswordResetViewTest(TestCase):
    fixtures = FIXTURES

    @classmethod
    def setUpTestData(cls):
        # создает пользователя
        cls.credentials = {"username": "bob_test", "password": "qwerty", "email": "test@test.ru"}
        cls.login_info = {"password": "qwerty", "email": "test@test.ru"}
        cls.user = User.objects.create_user(**cls.credentials)

    def test_reset_password_page(self):
        response = self.client.get(reverse("profiles:reset_password"))
        self.assertEqual(response.status_code, 200)

    def test_form_reset_password_page(self):
        response = self.client.post(reverse("profiles:reset_password"), data={"email": "test@test.ru"})
        # self.token = response.context[0].dicts[1]['token']
        # self.uid = response.context[0].dicts[1]['uid']
        self.assertEqual(response.status_code, 302)

    def test_reset_password_page2(self):
        response = self.client.get(reverse("profiles:reset_password_done"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Инструкция")

    def test_reset_password_page3(self):
        response = self.client.post(reverse("profiles:reset_password"), data={"email": "test@test.ru"})
        token = response.context[0].dicts[1]["token"]
        uid = response.context[0].dicts[1]["uid"]
        response = self.client.get(reverse("profiles:reset_password_confirm", kwargs={"uidb64": uid, "token": token}))
        self.assertEqual(response.status_code, 302)

    def test_post_reset_password_page3(self):
        response = self.client.post(reverse("profiles:reset_password"), data={"email": "test@test.ru"})
        token = response.context[0].dicts[1]["token"]
        uid = response.context[0].dicts[1]["uid"]
        response = self.client.post(
            reverse("profiles:reset_password_confirm", kwargs={"uidb64": uid, "token": token}),
            data={"password1": "ABC1abc1", "password2": "ABC1abc1"},
        )
        self.assertEqual(response.status_code, 302)

    def test_login_with_new_pass(self):
        response = self.client.post(reverse("profiles:reset_password"), data={"email": "test@test.ru"})
        token = response.context[0].dicts[1]["token"]
        uid = response.context[0].dicts[1]["uid"]
        response = self.client.get(
            reverse("profiles:reset_password_confirm", kwargs={"uidb64": uid, "token": token}),
        )
        response = self.client.post(response.url, data={"new_password1": "ABC1abc1", "new_password2": "ABC1abc1"})
        self.login_info["password"] = "ABC1abc1"
        islogin = self.client.login(**self.login_info)
        self.assertEqual(islogin, True)
