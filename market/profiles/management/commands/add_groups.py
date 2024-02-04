from django.contrib.auth.models import Permission, Group
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    A simple management command that adds groups with permissions
    to the admin panel.

    :arg:
    retailer (class Group): Seller's group with permission
      to add, view and modify products on the site.
    any_user (class Group): The user group allows you
      to view products and their details.

    permission_list_retailer (list): List of permissions for retailer.
    permission_list_any_user (list): List of permissions for any_user.
    """

    help = "Adds groups with permissions to the admin panel."

    def handle(self, *args, **options):
        # Added retailer group
        self.stdout.write("Start append retailer group")
        retailer, created = Group.objects.get_or_create(name="retailer")
        permission_list_retailer = [
            "add_detail",
            "view_detail",
            "add_product",
            "view_product",
            "add_productdetail",
            "change_productdetail",
            "delete_productdetail",
            "view_productdetail",
            "add_offer",
            "change_offer",
            "delete_offer",
            "view_offer",
            "view_shop",
        ]
        [retailer.permissions.add(Permission.objects.get(codename=perm)) for perm in permission_list_retailer]
        retailer.save()

        # Added any user group
        self.stdout.write("Start append any_user group")
        any_user, created = Group.objects.get_or_create(name="everyman")
        permission_list_any_user = ["view_productdetail", "view_product"]
        [any_user.permissions.add(Permission.objects.get(codename=perm)) for perm in permission_list_any_user]
        any_user.save()

        self.stdout.write("Groups retailer and any user added")
