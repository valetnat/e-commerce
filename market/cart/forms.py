from django import forms
from django.forms.widgets import HiddenInput

from shops.models import Offer


class UserOneOfferCARTForm(forms.Form):
    """Форма для добавления одной записи в корзину"""

    amount = forms.IntegerField(min_value=0)
    offer_id = forms.IntegerField()


class UserManyOffersCARTForm(forms.Form):
    """
    Форма для множественного добавления записей в корзину
    при этом поля должны содержать:
    offer_id[i]
    amount[i]
    """

    def __init__(self, number: int, *args, **kwargs):
        self.queryset = Offer.objects.prefetch_related("product").select_related("shop")
        super().__init__(*args, **kwargs)
        for i in range(number):
            self.fields[f"offer_id[{i}]"] = forms.IntegerField()
            self.fields[f"amount[{i}]"] = forms.IntegerField(
                min_value=0, max_value=self.get_offer(self.data[f"offer_id[{i}]"])
            )

    def get_offer(self, offer_id):
        offer_remains = self.queryset.get(pk=int(offer_id)).remains
        return offer_remains


class UserOneOfferCARTDeleteForm(forms.Form):
    """Форма для удаления"""

    offer_id = forms.IntegerField(min_value=0, widget=HiddenInput())
