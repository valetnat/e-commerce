from typing import Dict
from django.http import HttpRequest

from comparison.services import ComparisonService


def comparison_items(request: HttpRequest) -> Dict[str, ComparisonService]:
    """
    Контекстный процессор добавления сравнения
    """
    comparison = ComparisonService(request=request)
    return {"comparison": comparison}
