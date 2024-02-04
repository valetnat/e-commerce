from django import forms


class BancAccountForm(forms.Form):
    """Форма для банковского счета"""

    banc_account = forms.RegexField(regex=r"\d{4} \d{4}")
