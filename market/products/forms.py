from django import forms
from django.utils.translation import gettext_lazy as _


class ProductReviewForm(forms.Form):
    """Форма отзыва о товаре"""

    review_content = forms.CharField(
        max_length=512,
        label="",
        widget=forms.Textarea(attrs={"cols": "80", "rows": "3", "placeholder": _("Отзыв"), "class": "form-textarea"}),
    )
