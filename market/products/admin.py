from django.contrib import admin  # noqa F401
from django.db.models import QuerySet
from django.http import HttpRequest

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import (
    Category,
    Detail,
    Product,
    ProductDetail,
    ProductImage,
    Tag,
    Review,
    Banner,
    Manufacturer,
    LimitedOffer,
)


class DetailInline(admin.StackedInline):
    model = Product.details.through


class ProductImageInline(admin.StackedInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админ Продукты"""

    inlines = [DetailInline, ProductImageInline]

    list_display = (
        "pk",
        "name",
        "manufacturer",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)


@admin.register(Detail)
class DetailAdmin(admin.ModelAdmin):
    """Админ Свойство продуктов"""

    list_display = (
        "pk",
        "name",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)


@admin.register(ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    """Админ Значение свойства продукта"""

    list_display = ("pk", "product", "detail", "value")
    list_display_links = (
        "pk",
        "value",
    )
    ordering = ("pk",)


@admin.action(description=_("Архивировать категорию"))
def mark_archived_category(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True, modified_at=timezone.now())


@admin.action(description=_("Разархивировать категорию"))
def mark_unarchived_category(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False, modified_at=timezone.now())


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ Категория"""

    actions = [
        mark_archived_category,
        mark_unarchived_category,
    ]
    list_display = (
        "pk",
        "parent_name_id",
        "name",
        "icon",
        "created_at",
        "modified_at",
        "is_active",
        "archived",
        "foreground",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)
    empty_value_display = "NULL"
    search_fields = [
        "name",
    ]
    search_help_text = _("Поиск категории по названию")
    list_filter = (
        "created_at",
        "modified_at",
    )
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "name",
                    "parent",
                    "slug",
                    "foreground",
                ),
            },
        ),
        (
            _("Иконка"),
            {
                "fields": ("icon",),
            },
        ),
        (
            _("Статус категории"),
            {
                "fields": ("is_active",),
                "description": _("Поле используеться для задания статуса категории"),
            },
        ),
        (
            _("Дополнительные функции"),
            {
                "fields": ("archived",),
                "description": _("Поле 'архивировано' используеться для 'soft delete'"),
            },
        ),
    ]

    @admin.display(description=_("родительская категория"))
    def parent_name_id(self, obj: Category):
        if obj.parent is None:
            return
        return str(obj.parent.id)


# Регистрация модели тега
admin.site.register(Tag)


@admin.action(description=_("Архивировать отзыв"))
def mark_archived_review(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True, modified_at=timezone.now())


@admin.action(description=_("Разархивировать отзыв"))
def mark_unarchived_review(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False, modified_at=timezone.now())


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админ Отзыв"""

    actions = [
        mark_archived_review,
        mark_unarchived_review,
    ]

    list_display = (
        "pk",
        "user_id",
        "product_id",
        "short_review_content",
        "is_published",
        "created_at",
        "modified_at",
        "archived",
    )

    list_display_links = ("pk",)

    ordering = ("pk",)

    list_filter = (
        "created_at",
        "modified_at",
    )

    fieldsets = [
        (
            None,
            {
                "fields": ("user", "product", "review_content"),
            },
        ),
        (
            _("Статус публикации"),
            {
                "fields": ("is_published",),
            },
        ),
        (
            _("Дополнительные функции"),
            {
                "fields": ("archived",),
                "description": _("Поле 'архивировано' используеться для 'soft delete'"),
            },
        ),
    ]

    @admin.display(description=_("отзыв"))
    def short_review_content(self, obj: Review) -> str:
        if len(obj.review_content) > 50:
            return obj.review_content[:50] + "..."
        return obj.review_content


@admin.action(description=_("Архивировать производителя"))
def mark_archived_manufacturer(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True, modified_at=timezone.now())


@admin.action(description=_("Разархивировать производителя"))
def mark_unarchived_manufacturer(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False, modified_at=timezone.now())


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    """Админ Производитель"""

    actions = [mark_archived_manufacturer, mark_unarchived_manufacturer]

    list_display = (
        "pk",
        "name",
        "slug",
        "created_at",
        "modified_at",
        "archived",
    )

    list_display_links = (
        "pk",
        "name",
    )

    ordering = ("pk",)

    list_filter = (
        "created_at",
        "modified_at",
    )

    fieldsets = [
        (
            None,
            {
                "fields": ("name", "slug"),
            },
        ),
        (
            _("Дополнительные функции"),
            {
                "fields": ("archived",),
                "description": _("Поле 'архивировано' используеться для 'soft delete'"),
            },
        ),
    ]


@admin.action(description=_("Архивировать баннер"))
def mark_archived_banner(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True, modified_at=timezone.now())


@admin.action(description=_("Разархивировать баннер"))
def mark_unarchived_banner(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False, modified_at=timezone.now())


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """Админ Баннер"""

    actions = [
        mark_archived_category,
        mark_unarchived_category,
    ]
    list_display = (
        "pk",
        "name",
        "description",
        "image",
        "archived",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)


@admin.action(description=_("Архивировать ограниченное предложениеннер"))
def mark_archived_limited_offer(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True, modified_at=timezone.now())


@admin.action(description=_("Разархивировать ограниченное предложение"))
def mark_unarchived_limited_offer(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False, modified_at=timezone.now())


@admin.register(LimitedOffer)
class LimitedOfferAdmin(admin.ModelAdmin):
    """Админ Ограниченное предложение"""

    actions = [
        mark_archived_limited_offer,
        mark_unarchived_limited_offer,
    ]
    list_display = (
        "pk",
        "product_id",
        "end_date",
        "archived",
    )
    list_display_links = ("pk",)
    ordering = ("pk",)
