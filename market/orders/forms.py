from django import forms
from django.forms import TextInput, Textarea, RadioSelect
from orders.models import Order
from profiles.forms import UserRegisterForm
from profiles.models import User


class OrderStepTwoForm(forms.ModelForm):
    """Форма для обработки второго шага заказа товара"""

    class Meta:
        model = Order
        fields = (
            "delivery_type",
            "city",
            "address",
        )
        widgets = {
            "city": TextInput(attrs={"class": "form-input"}),
            "address": Textarea(attrs={"class": "form-textarea"}),
            "delivery_type": RadioSelect,
        }


class OrderStepThreeForm(forms.ModelForm):
    """Форма для обработки третьего шага заказа товара"""

    class Meta:
        model = Order
        fields = ("payment_type",)
        widgets = {
            "payment_type": RadioSelect,
        }


class OrderFastRegistrationAnonymousUser(UserRegisterForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
        ]


class OrderStepFourForm(forms.ModelForm):
    """
    Форма для обработки четвертого шага заказа товара.
    """

    class Meta:
        model = Order
        fields = (
            "delivery_type",
            "city",
            "address",
            "payment_type",
        )
