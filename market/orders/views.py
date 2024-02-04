from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, FormView
from orders.forms import OrderStepTwoForm, OrderStepThreeForm, OrderFastRegistrationAnonymousUser

from orders.models import Order, OrderDetail
from orders.services.services import OrderDetailCreate
from profiles.models import User
from profiles.views import UserRegisterView


class OrderDetailView(PermissionRequiredMixin, DetailView):
    """
    Страница отображения деталей заказа при переходе на заказ из истории заказов.
    """

    model = Order
    template_name = "orders/detail_order.jinja2"

    def has_permission(self):
        return self.get_object().user == self.request.user or self.request.user.is_superuser


class OrderStepOneView(LoginRequiredMixin, UserRegisterView):
    """
    Отображение первого шага заказа.
    Если пользователь зарегистрирован перенаправляет его сразу на следующий шаг.
    """

    template_name = "orders/order_step_one.jinja2"
    success_url = reverse_lazy("order:order_step_2")
    form_class = OrderFastRegistrationAnonymousUser

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("orders:view_step_two"))

        form = OrderFastRegistrationAnonymousUser()
        super().get(form)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class OrderStepTwoView(FormView):
    """Отображает страницу второго шага заказа"""

    form_class = OrderStepTwoForm
    template_name = "orders/order_step_two.jinja2"

    def form_valid(self, form):
        self.request.session["delivery_type"] = form.cleaned_data.get("delivery_type")
        self.request.session["city"] = form.cleaned_data.get("city")
        self.request.session["address"] = form.cleaned_data.get("address")
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if self.request.session.get("delivery_type"):
            initial["delivery_type"] = self.request.session.get("delivery_type")

        if self.request.session.get("city"):
            initial["city"] = self.request.session.get("city")

        if self.request.session.get("address"):
            initial["address"] = self.request.session.get("address")

        return initial

    def get_success_url(self):
        return reverse("orders:view_step_three")


class OrderStepThreeView(LoginRequiredMixin, FormView):
    """Отображает страницу третьего шага заказа"""

    form_class = OrderStepThreeForm
    template_name = "orders/order_step_three.jinja2"

    def form_valid(self, form):
        self.request.session["payment_type"] = form.cleaned_data["payment_type"]
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if self.request.session.get("payment_type"):
            initial["payment_type"] = self.request.session.get("payment_type")
        return initial

    def get_success_url(self):
        OrderDetailCreate(self.request).created_order_details_product()

        self.request.session["cart"] = None
        self.request.session["cart_size"] = None
        self.request.session["cart_price"] = None
        return reverse("orders:view_step_four")


class OrderStepFourView(ListView):
    """View - class для отображения четвёртого шага заказа."""

    model = OrderDetail
    template_name = "orders/order_step_four.jinja2"
    context_object_name = "products"

    def get_queryset(self):
        order = (
            Order.objects.prefetch_related("details")
            .select_related("user")
            .filter(user__pk=self.request.user.pk)
            .first()
        )
        queryset = order.details.all()
        return queryset


class OrderHistoryListView(ListView):
    """View - class для отображения истории заказов пользователя."""

    model = Order
    template_name = "orders/order_history.jinja2"
    context_object_name = "orders"

    def get_queryset(self):
        user = User.objects.get(pk=self.request.user.pk)
        queryset = (
            Order.objects.filter(user=user)
            .select_related("user")
            .prefetch_related(
                "details",
            )
        )
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["history"] = self.get_queryset()
        return context
