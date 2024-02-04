from django import forms


class CleanNoneValuesFromMixin:
    """Миксин очистки от пустых значений"""

    def clean(self):
        """Очистка от пустых значений"""

        cleaned_data = super().clean()  # type: ignore
        return {key: value for key, value in cleaned_data.items() if value}


class CatalogFilterForm(CleanNoneValuesFromMixin, forms.Form):
    """Форма фильтра каталога"""

    search = forms.CharField(max_length=256)

    price = forms.CharField(max_length=20)
    title = forms.CharField(max_length=256)
    remains = forms.BooleanField(required=False)
    free_delivery = forms.BooleanField(required=False)
