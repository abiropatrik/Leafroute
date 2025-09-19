from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from leafroute.apps.accounts.models import UserProfile

class Command(BaseCommand):
    help = "Set up groups and assign UserProfile permissions"

    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(UserProfile)

        # Get permissions
        org_perm = Permission.objects.get(codename="organiser_tasks", content_type=content_type)
        drv_perm = Permission.objects.get(codename="driver_tasks", content_type=content_type)
        wh_perm = Permission.objects.get(codename="warehouseman_tasks", content_type=content_type)
        mgr_perm = Permission.objects.get(codename="manager_tasks", content_type=content_type)

        # Organiser group (view + organiser tasks)
        organiser_group, _ = Group.objects.get_or_create(name="Organisers")
        organiser_group.permissions.add(org_perm)

        # Driver group (view + driver tasks)
        driver_group, _ = Group.objects.get_or_create(name="Drivers")
        driver_group.permissions.add(drv_perm)

        # Warehouseman group (view + warehouseman tasks)
        warehouseman_group, _ = Group.objects.get_or_create(name="Warehousemen")
        warehouseman_group.permissions.add(wh_perm)

        # Manager group (view + manager tasks)
        manager_group, _ = Group.objects.get_or_create(name="Managers")
        manager_group.permissions.add(mgr_perm)

        self.stdout.write(self.style.SUCCESS("Groups and permissions set up successfully"))
