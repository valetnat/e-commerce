from django.contrib.auth.models import Group
from django.contrib.auth.views import (
    LogoutView,
    PasswordChangeView,
    LoginView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.urls import reverse_lazy, reverse
from django.http.response import HttpResponseRedirect
from django.views.generic import TemplateView, CreateView, UpdateView, ListView
from django.contrib.auth.mixins import UserPassesTestMixin

from .forms import UserRegisterForm, ProfileAvatarUpdateForm, CustomSetPasswordForm
from .models import User
from products.models import Product
from .services.products_history import get_products_in_user_history
from products.services.product_price import product_min_price_or_none
from cart.services.cart_service import login_cart


class AboutUserView(TemplateView):
    """
    View class - информация о пользователе.
    Проверяем авторизован ли пользователь и имеет ли пользователь магазин.
    :context['shop'] (queryset | str): если пользователь имеет магазин,
      то в переменную возвращается queryset магазинов.
      Иначе возвращает пустую строку.
    :context['history'](queryset): если пользователь авторизован,
      то ему показаны последние 3 просмотренных товара.
    """

    template_name = "profiles/about-user.jinja2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update_avatar"] = ProfileAvatarUpdateForm()
        user = self.request.user

        if user.is_authenticated:
            history = get_products_in_user_history(user, number=3)
            context["history"] = history
        context["price"] = product_min_price_or_none
        return context

    def post(self, request):
        update_avatar = ProfileAvatarUpdateForm(request.POST, request.FILES)
        if update_avatar.is_valid():
            picture = update_avatar.cleaned_data.get("user_avatar")
            user = User.objects.get(pk=self.request.user.pk)
            user.avatar = picture
            user.save()
            return HttpResponseRedirect(reverse("profiles:about-user"))
        return HttpResponseRedirect(reverse("profiles:about-user"))


class HomePage(TemplateView):
    """View class заглушка - главная страница сайта."""

    template_name = "profiles/index.jinja2"


class UserRegisterView(CreateView):
    """
    View class для регистрации пользователей. Если данные из формы валидны,
    авторизовывает пользователя и перенаправляет на главную страницу сайта.
    """

    form_class = UserRegisterForm
    template_name = "profiles/register.jinja2"
    success_url = reverse_lazy("products:home-page")

    def get(self, request, **kwargs):
        form = UserRegisterForm()
        super().get(form)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)

        password = form.cleaned_data.get("password1")
        email = form.cleaned_data.get("email")
        retailer_group = form.cleaned_data.get("retailer_group")

        user = authenticate(
            self.request,
            email=email,
            password=password,
        )
        if retailer_group:
            group = Group.objects.get(name="retailer")
            if not user.is_staff:
                user.is_staff = True
            user.groups.add(group)
            user.save()
        login(request=self.request, user=user)
        return response


class UserLogoutView(LogoutView):
    """View class заглушка - user logout."""

    next_page = reverse_lazy("products:home-page")


class UserResetPasswordView(PasswordChangeView):
    """View class смены пароля. Запрашивает у пользователя старый пароль
    и новый пароль дважды.
    Если первый пароль совпадает со вторым, устанавливается новый пароль
    и отправляет пользователя на главную страницу.
    """

    template_name = "profiles/password_form.jinja2"
    success_url = reverse_lazy("products:home-page")


class UserUpdateProfileInfo(UpdateView):
    """View class обновления информации о пользователе."""

    model = User
    template_name = "profiles/user_update_form2.jinja2"
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("profiles:about-user")
    fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
        "residence",
        "address",
        "avatar",
    ]


class UserHistoryView(UserPassesTestMixin, ListView):
    template_name = "profiles/product-history.jinja2"
    model = Product
    context_object_name = "history"
    extra_context = {"price": product_min_price_or_none}

    def get_queryset(self):
        user = self.request.user
        return get_products_in_user_history(user)

    def test_func(self):
        return self.request.user.is_authenticated


class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        answer = super().post(request, *args, **kwargs)
        if self.request.user.is_authenticated:
            login_cart(self.request)
        return answer


class CustomPasswordResetView(PasswordResetView):
    subject_template_name = "profiles/password_reset_subject.txt"
    email_template_name = "profiles/password_reset_email.html"
    success_url = reverse_lazy("profiles:reset_password_done")
    template_name = "profiles/password_reset_form.jinja2"


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "profiles/password_reset_done.jinja2"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy("profiles:reset_password_complete")
    template_name = "profiles/password_reset_confirm.jinja2"
    form_class = CustomSetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_"] = self.user
        return context


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "profiles/password_reset_complete.jinja2"
