from rest_framework.serializers import ValidationError


def even_number(value):
    if value % 2 != 0:
        raise ValidationError("This field must be an even number.")
