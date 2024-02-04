from typing import Dict

from django.http import HttpRequest

from site_settings.models import SiteSettings


def site_settings(request: HttpRequest) -> Dict[str, SiteSettings]:
    """
    Контекстный процессор для получения настроек сайта
    """
    settings = SiteSettings.load()
    request.site_settings = settings
    return {"site_settings": settings}
