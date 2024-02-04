from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import redirect


def clear_all_cache_view(request) -> HttpResponseRedirect:
    """Очистка всего кеша"""
    cache.clear()
    messages.success(request, "All cache is cleared")
    return redirect(request.META.get("HTTP_REFERER"))
