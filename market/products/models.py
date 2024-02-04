import os
from typing import Union

from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.urls import reverse


def product_images_directory_path(instance: Union["Product", "ProductImage"], filename: str) -> str:
    """Функция получения пути для изображений продукта и превью продукта"""
    if isinstance(instance, ProductImage):
        return "img/products/{name}/{filename}".format(name=instance.product.name, filename=filename)
    return "img/products/{name}/preview_{filename}".format(name=instance.name, filename=filename)


class ProductImage(models.Model):
    """Изображение для продукта"""

    product = models.ForeignKey(
        null=False,
        on_delete=models.CASCADE,
        to="Product",
        verbose_name="продукт",
        related_name="images",
    )
    image = models.ImageField(null=True, blank=True, upload_to=product_images_directory_path)

    class Meta:
        verbose_name = _("изображение")
        verbose_name_plural = _("изображения")

    def delete(self, using=None, keep_parents=False):
        """Удаление файла изображения при удалении экземпляра модели"""
        try:
            os.remove(f"{settings.MEDIA_ROOT}/{self.image}")
        except FileNotFoundError:
            pass
        finally:
            return super().delete(using, keep_parents)


class Product(models.Model):
    """Продукт"""

    class Meta:
        verbose_name = _("продукт")
        verbose_name_plural = _("продукты")

    name = models.CharField(max_length=512, unique=True, verbose_name=_("наименование"))
    manufacturer = models.ForeignKey("Manufacturer", on_delete=models.CASCADE, verbose_name=_("производитель"))
    details = models.ManyToManyField("Detail", through="ProductDetail", verbose_name=_("характеристики"))
    about = models.TextField(blank=True, max_length=512, verbose_name="краткое описание")
    description = models.TextField(blank=True, max_length=1024, verbose_name="описание")
    category = models.ForeignKey(on_delete=models.PROTECT, to="products.category", verbose_name="категория товаров")
    preview = models.ImageField(null=True, blank=True, upload_to=product_images_directory_path)
    tags = models.ManyToManyField(to="Tag", verbose_name=_("теги"), related_name="products", blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Попутное создание экземпляра ProductImage от preview"""
        super().save(force_insert, force_update, using, update_fields)
        if self.preview:
            ProductImage.objects.get_or_create(product=self, image=self.preview)

    def get_absolute_url(self):
        """Method returns a string that can be used to refer to the object over HTTP"""
        return reverse("products:product-detail", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return f"Товар(pk={self.pk}, name={self.name!r})"


class Tag(models.Model):
    """Модель Тег"""

    name = models.CharField(max_length=64, verbose_name=_("название тега"))

    def __str__(self) -> str:
        return f"Тег (pk={self.pk}, name={self.name!r})"


class Detail(models.Model):
    """Свойство продукта"""

    name = models.CharField(max_length=512, verbose_name=_("наименование"))

    class Meta:
        verbose_name = _("свойство продуктов")
        verbose_name_plural = _("свойства продуктов")

    def __str__(self) -> str:
        return f"Детали продукта (pk={self.pk}, name={self.name!r})"


class ProductDetail(models.Model):
    """Значение свойства продукта"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    detail = models.ForeignKey(Detail, on_delete=models.CASCADE, related_name="product_value")
    value = models.CharField(max_length=128, verbose_name=_("значение"))

    class Meta:
        verbose_name = _("значение свойства продуктов")
        verbose_name_plural = _("значения свойства продуктов")
        constraints = [UniqueConstraint(fields=["product", "detail"], name="unique_product_detail")]


def category_icon_directory_path(instance: "Category", filename: str) -> str:
    """Функция получения пути для иконок категорий"""
    return "img/icons/categories/{slug}/{filename}".format(
        slug=instance.slug,
        filename=filename,
    )


class Category(models.Model):
    """Категория продукта"""

    name = models.CharField(max_length=128, unique=True, verbose_name=_("наименование"))
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("дата создания"))
    modified_at = models.DateTimeField(auto_now=True, verbose_name=_("дата последнего изменения"))
    archived = models.BooleanField(default=False, verbose_name=_("архивировано"))
    is_active = models.BooleanField(default=True, verbose_name=_("активно"))
    parent = models.ForeignKey("self", blank=True, null=True, verbose_name=_("родитель"), on_delete=models.CASCADE)
    foreground = models.BooleanField(default=False, verbose_name=_("приоритетный"))
    icon = models.FileField(
        null=True,
        blank=True,
        upload_to=category_icon_directory_path,
        verbose_name=_("иконка"),
        validators=[FileExtensionValidator(["svg", "img", "png"])],
    )

    class Meta:
        verbose_name = _("категория")
        verbose_name_plural = _("категории")
        app_label = "products"
        constraints = [UniqueConstraint(fields=["name", "parent"], name="unique_parent_name")]

    def get_absolute_url(self):
        """Method returns a string that can be used to refer to the object over HTTP"""
        return reverse("catalog:index") + f"?category_id={self.pk}"

    def get_icon_name(self) -> str:
        """
        Получение названия файла иконки
        :return: название файла
        """
        return os.path.basename(self.icon.name)

    def __str__(self) -> str:
        return f"Категория (pk={self.pk}, name={self.name!r})"


class Review(models.Model):
    """Отзыв на продукт"""

    class Meta:
        verbose_name = _("отзыв")
        verbose_name_plural = _("отзывы")
        app_label = "products"

    user = models.ForeignKey("profiles.User", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review_content = models.TextField(verbose_name=_("отзыв"))
    is_published = models.BooleanField(default=False, verbose_name=_("опубликовано"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("дата создания"))
    modified_at = models.DateTimeField(auto_now=True, verbose_name=_("дата последнего изменения"))
    archived = models.BooleanField(default=False, verbose_name=_("архивировано"))

    def __str__(self) -> str:
        return f"Отзыв (pk={self.pk}, product_id={self.product.id})"


class Manufacturer(models.Model):
    class Meta:
        verbose_name = _("производитель")
        verbose_name_plural = _("производители")

    name = models.CharField(max_length=128, unique=True, verbose_name=_("производитель"))
    slug = models.SlugField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("дата создания"))
    modified_at = models.DateTimeField(auto_now=True, verbose_name=_("дата последнего изменения"))
    archived = models.BooleanField(default=False, verbose_name=_("архивировано"))

    def __str__(self) -> str:
        return f"Производитель(pk={self.pk}, name={self.name!r})"


def banner_directory_path(instance: "Banner", filename: str) -> str:
    return "img/banner/{filename}".format(
        filename=filename,
    )


class Banner(models.Model):
    """Баннер"""

    class Meta:
        verbose_name = _("баннер")
        verbose_name_plural = _("баннеры")

        constraints = [
            models.CheckConstraint(  # type: ignore
                check=models.Q(category__isnull=False, product__isnull=True, offer__isnull=True)
                | models.Q(category__isnull=True, product__isnull=False, offer__isnull=True)
                | models.Q(category__isnull=True, product__isnull=True, offer__isnull=False),
                name="category_or_product_or_offer",
                violation_error_message="Должно быть заполнено только одно поле.",
            ),
        ]

    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    description = models.TextField(blank=True, max_length=512, verbose_name=_("описание"))
    image = models.ImageField(null=True, blank=True, upload_to=banner_directory_path)
    archived = models.BooleanField(default=False, verbose_name=_("архивировано"))
    category = models.ForeignKey(
        null=True, blank=True, on_delete=models.PROTECT, to="products.category", verbose_name="категория товаров"
    )
    product = models.ForeignKey(
        null=True, blank=True, on_delete=models.PROTECT, to="products.product", verbose_name="товар"
    )
    offer = models.ForeignKey(
        null=True, blank=True, on_delete=models.PROTECT, to="shops.offer", verbose_name="предложение магазина"
    )

    def __str__(self) -> str:
        return f"Баннер (pk={self.pk}, name={self.name!r})"

    def delete(self, using=None, keep_parents=False):
        """Удаление файла изображения при удалении экземпляра модели"""
        path = f"{settings.MEDIA_ROOT}/{self.image}"
        if os.path.isfile(path):
            os.remove(path)


class LimitedOffer(models.Model):
    """Ограниченные предложения"""

    class Meta:
        verbose_name = _("ограниченное предложение")
        verbose_name_plural = _("ограниченные предложения")

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    end_date = models.DateTimeField(null=False, verbose_name=_("дата окончания"))
    archived = models.BooleanField(default=False, verbose_name=_("архивировано"))

    def __str__(self) -> str:
        return f"Ограниченное предложение (pk={self.pk}, product_id={self.product.id})"
