from django.core.cache import cache
from django.test import TestCase
from profiles.models import UserProductHistory, User
from products.models import Product, Category, Detail, Manufacturer


class UserProductHistoryTest(TestCase):
    """Класс тестов для записей в истории посещения пользователя"""

    @classmethod
    def setUpTestData(cls):
        cls.all_info = {
            "username": "John-for-test",
            "phone": "89701112233",
            "residence": "London",
            "address": "Bakers streets 148 ap.3",
            "retailer_group": True,
        }
        cls.user_login_info = {
            "email": "jhon@fortest.com",
            "password": "JohnforTest1234",
        }

        cls.user = User.objects.create_user(
            username=cls.all_info["username"],
            email=cls.user_login_info["email"],
            password=cls.user_login_info["password"],
            phone=cls.all_info["phone"],
            residence=cls.all_info["residence"],
            address=cls.all_info["address"],
        )

        cls.category = Category.objects.create(name="Тестовая категория")
        cls.manufacturer = Manufacturer.objects.create(name="tecтовый производитель")
        cls.detail = Detail.objects.create(name="тестовая характеристика")
        cls.product = Product.objects.create(
            name="Тестовый продукт", category=cls.category, manufacturer=cls.manufacturer
        )
        cls.product.details.set([cls.detail], through_defaults={"value": "тестовое значение"})

        cls.user.product_in_history.add(cls.product)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cache.clear()

    def test_create_object(self):
        record = UserProductHistory.objects.filter(user=self.user, product=self.product)[0]
        self.assertIsInstance(record, UserProductHistory)

    def test_related_name(self):
        records = self.user.history_record.all()
        record = UserProductHistory.objects.filter(user=self.user, product=self.product)[0]
        self.assertIn(record, records)

    def test_field_name(self):
        record = UserProductHistory.objects.filter(user=self.user, product=self.product)[0]
        attr_names = dir(record)
        variable_name_in_service = ("time", "product", "user")
        for name in variable_name_in_service:
            self.assertIn(name, attr_names)
