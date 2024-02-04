from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from products.models import Product, Detail, ProductDetail, Category, ProductImage, Tag, Review, Manufacturer, Banner


User = get_user_model()


class ProductModelTest(TestCase):
    """Класс тестов модели Продукт"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Тестовая категория")
        cls.manufacturer = Manufacturer.objects.create(name="tecтовый производитель")
        cls.detail = Detail.objects.create(name="тестовая характеристика")
        cls.product = Product.objects.create(
            name="Тестовый продукт", category=cls.category, manufacturer=cls.manufacturer
        )
        cls.product.details.set([cls.detail], through_defaults={"value": "тестовое значение"})

    def test_verbose_name(self):
        product = ProductModelTest.product
        field_verboses = {
            "name": "наименование",
            "details": "характеристики",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(product._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        product = ProductModelTest.product
        max_length = product._meta.get_field("name").max_length
        self.assertEqual(max_length, 512)

    def test_productdetail_value(self):
        productdetail = ProductDetail.objects.all()[0]
        value = productdetail.value
        self.assertEqual(value, "тестовое значение")

    def test_product_fields_name(self):
        attr_names = dir(Product())
        variable_name_in_template = (
            "shops",
            "preview",
            "images",
            "name",
            "about",
            "tags",
            "description",
            "offers",
            "productdetail_set",
        )
        for name in variable_name_in_template:
            self.assertIn(name, attr_names)


class TagModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tag = Tag.objects.create(name="тестовый тег")

    def test_verbose_name(self):
        tag = self.tag
        field_verboses = {
            "name": "название тега",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(tag._meta.get_field(field).verbose_name, expected_value)


class ProductImageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Тестовая категория")
        cls.manufacturer = Manufacturer.objects.create(name="tecтовый производитель")
        cls.product = Product.objects.create(name="test_product", category=cls.category, manufacturer=cls.manufacturer)
        cls.image_file_name = "test_img.jpg"
        img_file = SimpleUploadedFile(
            name=cls.image_file_name,
            content=open("products/tests/test_img.jpg", "rb").read(),
            content_type="image/jpeg",
        )

        cls.productimage = ProductImage.objects.create(image=img_file, product=cls.product)

    def test_verbose_name(self):
        image = self.productimage
        field_verboses = {
            "product": "продукт",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(image._meta.get_field(field).verbose_name, expected_value)

    def test_image_path(self):
        image = self.productimage
        path = image.image.url
        expected_path = f"/media/img/products/{self.product.name}/{self.image_file_name}"
        self.assertEqual(path, expected_path)
        self.productimage.delete()


class DetailModelTest(TestCase):
    """Класс тестов модели Свойство продукта"""

    @classmethod
    def setUpTestData(cls):
        cls.detail = Detail.objects.create(name="тестовая характеристика")

    def test_verbose_name(self):
        detail = DetailModelTest.detail
        field_verboses = {
            "name": "наименование",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(detail._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        detail = DetailModelTest.detail
        max_length = detail._meta.get_field("name").max_length
        self.assertEqual(max_length, 512)


class ProductDetailModelTest(TestCase):
    """Класс тестов модели Значение свойства продукта"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Тестовая категория")
        cls.detail = Detail.objects.create(name="тестовая характеристика")
        cls.manufacturer = Manufacturer.objects.create(name="tecтовый производитель")
        cls.product = Product.objects.create(
            name="Тестовый продукт", category=cls.category, manufacturer=cls.manufacturer
        )
        cls.product_detail = ProductDetail.objects.create(
            product=cls.product,
            detail=cls.detail,
            value="тестовое значение характеристики",
        )

    def test_verbose_name(self):
        product_detail = ProductDetailModelTest.product_detail
        field_verboses = {
            "value": "значение",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(product_detail._meta.get_field(field).verbose_name, expected_value)

    def test_value_max_length(self):
        product_detail = ProductDetailModelTest.product_detail
        max_length = product_detail._meta.get_field("value").max_length
        self.assertEqual(max_length, 128)


class CategoryModelTest(TestCase):
    """Класс тестов модели Категория продуктов"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Тестовая категория продукта",
        )

        cls.subcategory = Category.objects.create(name="Тестовая подкатегория продукта", parent=cls.category)

    def test_verbose_name(self):
        category = CategoryModelTest.category
        field_verboses = {
            "name": "наименование",
            "parent": "родитель",
            "slug": "slug",
            "created_at": "дата создания",
            "modified_at": "дата последнего изменения",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(category._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        category = self.category
        max_length = category._meta.get_field("name").max_length
        self.assertEqual(max_length, 128)

    def test_parent_null(self):
        category = CategoryModelTest.category
        null = category._meta.get_field("parent").null
        self.assertEqual(null, True)

    def test_name_unique(self):
        category = CategoryModelTest.category
        unique = category._meta.get_field("name").unique
        self.assertEqual(unique, True)

    def test_archived_default(self):
        category = CategoryModelTest.category
        default = category._meta.get_field("archived").default
        self.assertEqual(default, False)

    def test_created_at_auto_now_add(self):
        category = CategoryModelTest.category
        auto_now_add = category._meta.get_field("created_at").auto_now_add
        self.assertEqual(auto_now_add, True)

    def test_modified_at_auto_now(self):
        category = CategoryModelTest.category
        auto_now = category._meta.get_field("modified_at").auto_now
        self.assertEqual(auto_now, True)

    def test_parent_foreign_key(self):
        category = CategoryModelTest.category
        subcategory = CategoryModelTest.subcategory
        self.assertEqual(subcategory.parent.pk, category.pk)


class ReviewModelTest(TestCase):
    """Класс тестов модели Отзывов"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Тестовая категория")
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

    def test_verbose_name(self):
        review = ReviewModelTest.review
        field_verboses = {
            "user": "user",
            "product": "product",
            "review_content": "отзыв",
            "is_published": "опубликовано",
            "created_at": "дата создания",
            "modified_at": "дата последнего изменения",
            "archived": "архивировано",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(review._meta.get_field(field).verbose_name, expected_value)


class BannerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Тестовая категория")
        cls.image_file_name = "test_img.jpg"
        img_file = SimpleUploadedFile(
            name=cls.image_file_name,
            content=open("products/tests/test_img.jpg", "rb").read(),
            content_type="image/jpeg",
        )
        cls.banner = Banner.objects.create(
            name="тестовое", description="тестовое", image=img_file, category=cls.category
        )

    def test_verbose_name(self):
        banner = self.banner
        field_verboses = {
            "name": "наименование",
            "description": "описание",
            "archived": "архивировано",
            "category": "категория товаров",
            "product": "товар",
            "offer": "предложение магазина",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(banner._meta.get_field(field).verbose_name, expected_value)

    def test_image(self):
        banner = self.banner
        path = banner.image.url
        expected_path = f"/media/img/banner/{self.image_file_name}"
        self.assertEqual(path, expected_path)
        self.banner.delete()
