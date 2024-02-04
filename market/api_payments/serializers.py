from rest_framework import serializers
from .custom_validators import even_number


class MeganoOrderEvenSerializer(serializers.Serializer):
    """Сериализатор для сервиса оплаты"""

    identify_number = serializers.IntegerField()
    cart_number = serializers.IntegerField(
        min_value=10000000,
        max_value=99999999,
        validators=[
            even_number,
        ],
    )
    price = serializers.DecimalField(max_digits=None, decimal_places=2)
