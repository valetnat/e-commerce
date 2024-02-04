from django import forms


class ComparisonForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())


class ComparisonDiffForm(forms.Form):
    different = forms.IntegerField(widget=forms.HiddenInput())
