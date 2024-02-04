from typing import Any, Dict
from django.db.models import QuerySet, Prefetch
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from catalog.context import CatalogContextProcessor
from catalog.utils import Params
from catalog.forms import CatalogFilterForm
from products.models import Tag
from shops.models import Offer
from site_settings.models import SiteSettings


class CatalogListView(ListView):
    """Страница каталога товаров"""

    template_name = "catalog/catalog.jinja2"
    context_object_name = "object_list"

    @property
    def site_settings(self) -> SiteSettings:
        """Получение настроек"""
        return SiteSettings.load()

    def get_queryset(self) -> QuerySet:
        """Создание запроса"""
        fields = [
            "pk",
            "price",
            "shop_id",
            "product_id",
            "remains",
            "delivery_method",
            "product__name",
            "product__about",
            "product__preview",
            "product__review",
            "product__manufacturer",
            "product__manufacturer__modified_at",
            "product__manufacturer__archived",
            "product__category",
            "product__category__name",
            "product__category__is_active",
            "product__category__archived",
        ]
        select_related_fields = [
            "product",
            "product__manufacturer",
            "product__category",
            "shop",
        ]

        queryset = Offer.objects.select_related(*select_related_fields).filter(remains__gt=0)
        params = Params(**self.request.GET.dict())
        context_proc = CatalogContextProcessor(self.request, {}, params, self.site_settings)

        tag_id = params.get("tag_id")

        if tag_id:
            queryset = queryset.prefetch_related(self.__get_tags_prefetch(tag_id))

        queryset = self._filter(queryset, context_proc)
        queryset = self._sort(queryset, context_proc)

        return queryset.only(*fields)

    def get_paginate_by(self, queryset: QuerySet) -> int:
        """Получение лимита пагинации"""
        return self.site_settings.paginate_by

    def __get_tags_prefetch(self, tag_id: str) -> Prefetch:
        """Получение тегов"""
        fields = ["pk", "name"]
        queryset = Tag.objects.filter(pk=tag_id).only(*fields)
        return Prefetch("product__tags", queryset=queryset)

    def _filter(self, queryset: QuerySet, proc: CatalogContextProcessor) -> QuerySet:
        """Фильтрация запроса"""
        queryset = proc.filter.filter_offer(queryset)
        queryset = proc.filter.filter_category(queryset)
        queryset = proc.filter.filter_tags(queryset)
        return proc.filter.filter_prodict(queryset)

    def _sort(self, queryset: QuerySet, proc: CatalogContextProcessor) -> QuerySet:
        """Сортировка запроса"""
        sort_ = proc.params.get("sort")
        desc_ = proc.params.get("desc")
        return proc.sorter.sort(self.site_settings.default_sort, queryset, sort_, desc_)

    def get_context_data(self, *, object_list=None, **kwargs) -> Dict[str, Any]:
        """Формирование контекста"""
        context = super().get_context_data(object_list=object_list, **kwargs)

        context_proc = CatalogContextProcessor(
            self.request,
            context,
            Params(**self.request.GET.dict()),
            self.site_settings,
        )
        context_proc.set_filter_context()
        context_proc.set_pagination_context()
        context_proc.set_context()

        return context_proc.context


class CatalogFilteredView(View):
    @property
    def site_settings(self) -> SiteSettings:
        """Получение настроек"""
        return SiteSettings.load()

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:  # noqa
        """Обработка POST запроса"""
        form = CatalogFilterForm(request.POST)
        form.is_valid()

        context_proc = CatalogContextProcessor(
            request,
            {},
            Params(**request.GET.dict()),
            self.site_settings,
        )
        context_proc.set_filter_context(form.cleaned_data)
        context_proc.set_context()

        url = reverse("catalog:index")

        params = context_proc.context.get("params")

        if params:
            url += params.to_string("?")

        return redirect(url, permanent=True)


class CatalogHomeView(View):
    """Класс маршрутизации запросов к каталогу"""

    def get(self, request, *args, **kwargs):
        """Обработка GET запроса"""
        view = CatalogListView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Обработка POST запроса"""
        view = CatalogFilteredView.as_view()
        return view(request, *args, **kwargs)
