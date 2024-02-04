from django.core.management import BaseCommand
from django.core import management


class Command(BaseCommand):
    """
    Команда для массового создания фикстур.
    """

    def handle(self, *args, **kwargs):
        fixtures_dict = {
            # "contenttypes": "0-contenttypes.json",
            # "auth": "00-groups_and_permissions.json",
            "user": "01-users.json",
            "shops.shop": "04-shops.json",
            "products.category": "05-category.json",
            "products.manufacturer": "06-manufacturer.json",
            "products.tag": "07-tags.json",
            "products.product": "08-products.json",
            "shops.offer": "09-offers.json",
            "products.detail": "10-details.json",
            "products.productimage": "11-productimages.json",
            "products.productdetail": "12-productdetails.json",
            "products.review": "13-reviews.json",
            "products.banner": "14-banners.json",
        }
        for model_name, file_name in fixtures_dict.items():
            management.call_command("loaddata", f"fixtures/{file_name}")
