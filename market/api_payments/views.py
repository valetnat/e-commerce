from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from .serializers import MeganoOrderEvenSerializer
from .services.errors import get_random_error


@api_view(
    [
        "POST",
    ]
)
def megano_fake_pay(request: Request) -> Response:
    """АПИ для ответа сервису оплаты"""
    data = request.data
    order_even = MeganoOrderEvenSerializer(data=data)
    if order_even.is_valid():
        return Response({"successfully": True, "error": ""}, status=200)
    else:
        return Response({"successfully": False, "error": f"{get_random_error()}"}, status=401)
