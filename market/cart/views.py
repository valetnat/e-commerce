from decimal import Decimal

from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from django.http import Http404, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin

from shops.models import Offer
from .forms import UserOneOfferCARTForm
from .services.cart_service import get_cart_service
from .forms import UserOneOfferCARTDeleteForm, UserManyOffersCARTForm
from discount.services import CartDiscount


class CartListView(TemplateView):
    """Отображение корзины пользователя и обновление корзины"""

    template_name = "cart/cart.jinja2"

    def get(self, request, *args, **kwargs):
        self.cart_service = get_cart_service(request)
        self.cart = self.cart_service.get_cart_as_dict()
        self.discount_service = CartDiscount(self.cart_service)
        self.discount = self.discount_service.get_discount()
        response = super().get(request, *args, **kwargs)
        return response

    def post(self, request, *args, **kwargs):
        self.cart_service = get_cart_service(request)
        number = self.cart_service.get_offers_len()
        form = UserManyOffersCARTForm(self.cart_service.get_offers_len(), request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            data = {form_data[f"offer_id[{i}]"]: form_data[f"amount[{i}]"] for i in range(number)}
            self.cart_service.update_cart(data)
            if kwargs["action"] == kwargs["buttons"][2]:
                return redirect("orders:view_step_one")
            return self.get(request, *args, **kwargs)
        else:
            return HttpResponse(form.errors.as_ul(), status=400)

    def get_queryset(self):
        offers_pk_list = self.cart.keys()
        queryset = Offer.objects.filter(pk__in=offers_pk_list).select_related("product", "shop")
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            "offer_list": self.get_queryset(),
            "cart": self.cart,
            "discount_amount": self.discount["sale"],
            "total_price": round((Decimal(self.cart_service.get_upd_price()) - Decimal(self.discount["sale"])), 2),
            "discount_name": self.discount["name"],
            "discount_value": self.discount["value"],
            "discount_weight": self.discount["weight"],
        }
        context.update(kwargs)
        return super().get_context_data(object_list=None, **context)


class RemoveCartView(View):
    """Очистка всей корзины"""

    def post(self, request, *args, **kwargs):
        self.cart_service = get_cart_service(request)
        self.cart_service.clear()
        return redirect("cart:user_cart")

    def get(self, request, *args, **kwargs):
        self.cart_service = get_cart_service(request)
        self.cart_service.clear()
        return redirect(request.META["HTTP_REFERER"])


class RemoveOneCartView(View):
    """Удаление из корзины одной записи предложения"""

    def get(self, request, *args, **kwargs):
        form = UserOneOfferCARTDeleteForm(request.GET)
        if form.is_valid():
            self.cart_service = get_cart_service(request)
            self.cart_service.remove_from_cart(**form.cleaned_data)
        return redirect("cart:user_cart")
        # raise Http404


class AddCartFromProduct(TemplateResponseMixin, FormMixin, View):
    template_name = "cart/invalid_cart_add.html"

    def get(self, request, *args, **kwargs):
        """Не допустимый метод"""
        raise Http404

    def post(self, request, *args, **kwargs):
        """Обработка формы для добавления предложения в корзину"""
        form = UserOneOfferCARTForm(request.POST)
        self.url = request.META["HTTP_REFERER"]
        self.cart_service = get_cart_service(request)
        if form.is_valid():
            self.cart_service.add_to_cart(**form.cleaned_data)
            return redirect(self.url + "#modal_open")
        else:
            return self.form_invalid(form)


class CartView(View):
    """
    Представление в котором:
        - при полечении "GET" запроса возвращается корзина пользователя
        - при полечении "POST" запроса возвращается обновленная кориза пользователя
        - переход в сервис оформления заказов
    """

    BUTTONS = (
        _("Удалить корзину"),
        _("Обновить корзину"),
        _("Оформить заказ"),
    )

    def get(self, request, *args, **kwargs):
        view = CartListView.as_view()
        return view(request, *args, buttons=self.BUTTONS, **kwargs)

    def post(self, request, *args, **kwargs):
        choice = {
            self.BUTTONS[0]: RemoveCartView.as_view(),  # Удалить корзину
            self.BUTTONS[1]: CartListView.as_view(),  # Обновить корзину
            self.BUTTONS[2]: CartListView.as_view(),  # Обновить корзину
        }
        action = request.POST.get("action")

        # Переход в оформление заказа
        # if action == self.BUTTONS[2]:
        #     return redirect("orders:view_step_one")

        view = choice.get(action)
        return view(request, *args, buttons=self.BUTTONS, action=action, **kwargs)
