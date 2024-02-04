from django import forms
from django.contrib.auth.forms import BaseUserCreationForm, UsernameField, SetPasswordForm

from django.utils.translation import gettext_lazy as _
from .models import User
from django.core.validators import RegexValidator


class UserRegisterForm(BaseUserCreationForm):
    """
    Форма регистрации пользователя. Запрашивает все необходимые данные.
    Запрашивает у пользователя, хочет ли он стать продавцом на сайте или нет.
    """

    phone = forms.CharField(
        label="Номер телефона",
        max_length=16,
        widget=forms.PasswordInput(
            attrs={"placeholder": "+7(999)999-99-99", "type": "text", "data-mask": "+7(999)999-99-99"}
        ),
        help_text="Вводите номер в виде '+7(ХХХ)ХХХ-ХХ-ХХ'",
        validators=[
            RegexValidator(regex=r"\+[7]\([0-9]{3}\)[0-9]{3}\-[0-9]{2}\-[0-9]{2}", message=_("номер некорректный"))
        ],
    )
    residence = forms.CharField(max_length=80, label="Город проживания")
    address = forms.CharField(
        max_length=80,
        label="Адрес доставки",
        widget=forms.Textarea(attrs={"cols": "60", "rows": "5"}),
    )
    retailer_group = forms.BooleanField(
        initial=False,
        required=False,
        label="Выбрать, если вы хотите стать продавцом на сайте",
    )
    error_messages = {
        "password_mismatch": "Два пароля не совпали.",
    }
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "новый пароль"}),
        help_text="<ul><li>Ваш пароль не должен быть слишком похож на другую "
        "вашу личную информацию.</li>"
        "<li>Ваш пароль должен содержать не менее 8 символов.</li>"
        "<li>Ваш пароль не может быть часто используемым паролем.</li>"
        "<li>Ваш пароль не может быть полностью цифровым.</li></ul>",
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"autocomplete": "новый пароль"}),
        strip=False,
        help_text="Введите тот же пароль, что и раньше, для проверки.",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "residence",
            "address",
            "retailer_group",
        ]

        field_classes = {
            "username": UsernameField,
            "first_name": forms.CharField,
            "last_name": forms.CharField,
            "email": forms.EmailField,
            "phone": forms.CharField,
            "residence": forms.CharField,
            "address": forms.CharField,
            "retailer_group": forms.BooleanField,
            "password1": forms.CharField,
        }


class ChangeProfileInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "residence",
            "address",
        ]


class ProfileAvatarUpdateForm(forms.Form):
    user_avatar = forms.ImageField()


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )
