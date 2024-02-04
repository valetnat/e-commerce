from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin
from products.models import Product
from .services import ComparisonService
from .forms import ComparisonForm, ComparisonDiffForm

from django.utils.translation import gettext_lazy as _


class ComparisonTemplateView(FormMixin, TemplateView):
    template_name = "comparison/comparison.jinja2"
    form_class = ComparisonDiffForm
    success_url = reverse_lazy("comparison:comparison")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comparison = ComparisonService(request=self.request)
        valid_list = comparison.get_valid_products_list()
        unique_details = comparison.get_all_unique_details(valid_list=valid_list)
        common, diff = comparison.get_common_diff_details(details_to_compare=unique_details, valid_list=valid_list)

        if len(valid_list) == 0:
            context["error"] = _("Нет товаров для сравнения")

        elif len(valid_list) == 1:
            context["objects_list"] = comparison.comparison
            context["error"] = _("Недостаточно данных для сравнения.")

        elif len(common) < 1:
            context["error"] = _("Невозможно сравнить то, что не сравнивается.")
            context["objects_list"] = comparison.comparison

        else:
            context["objects_list"] = comparison.compare(details_to_compare=unique_details, valid_list=valid_list)
            context["common"], context["diff"] = common, diff

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = self.get_form()

        if form.is_valid():
            cd = form.cleaned_data["different"]
            context["display_diff_details"] = cd

        return self.render_to_response(context)


class ComparisonAddView(View):
    def post(self, request, *args, **kwargs):
        comparison = ComparisonService(request=request)
        form = ComparisonForm(request.POST)
        url = request.META["HTTP_REFERER"]

        if form.is_valid():
            cd = form.cleaned_data
            product = get_object_or_404(Product, pk=cd["product_id"])
            res = comparison.add(product=product)

            if res:
                return redirect(url + "#modal_open_comparison_succ")
            else:
                return redirect(url + "#modal_open_comparison_failed")


class ComparisonDeleteView(View):
    def get(self, request, *args, **kwargs):
        comparison = ComparisonService(request=request)
        comparison.clear()

        return redirect("comparison:comparison")

    def post(self, request, *args, **kwargs):
        comparison = ComparisonService(request=request)
        form = ComparisonForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            product = get_object_or_404(Product, pk=cd["product_id"])
            comparison.remove(product=product)

        return redirect("comparison:comparison")
