from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = "Create initial demo users"

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        organiser_group, _ = Group.objects.get_or_create(name="Organisers")
        driver_group, _ = Group.objects.get_or_create(name="Drivers")
        warehouseman_group, _ = Group.objects.get_or_create(name="Warehousemen")
        manager_group, _ = Group.objects.get_or_create(name="Managers")

        #main demo users:
        if not User.objects.filter(username="d_admin").exists():
            user = User.objects.create_superuser(
                username="d_admin",
                email="d_admin@leafroute.com",
                password="szakdoga",
                first_name="Adam",
                last_name="Admin"
            )
            user.groups.add(admin_group)

        if not User.objects.filter(username="d_organiser").exists():
            user = User.objects.create_user(
                username="d_organiser",
                email="d_organiser@leafroute.com",
                password="szakdoga",
                first_name="Otto",
                last_name="Organiser"
            )
            user.groups.add(organiser_group)

        if not User.objects.filter(username="d_driver").exists():
            user = User.objects.create_user(
                username="d_driver",
                email="d_driver@leafroute.com",
                password="szakdoga",
                first_name="David",
                last_name="Driver"
            )
            user.groups.add(driver_group)

        if not User.objects.filter(username="d_warehouseman").exists():
            user = User.objects.create_user(
                username="d_warehouseman",
                email="d_warehouseman@leafroute.com",
                password="szakdoga",
                first_name="William",
                last_name="Warehouseman"
            )
            user.groups.add(warehouseman_group)

        if not User.objects.filter(username="d_manager").exists():
            user = User.objects.create_user(
                username="d_manager",
                email="d_manager@leafroute.com",
                password="szakdoga",
                first_name="Michael",
                last_name="Manager"
            )
            user.groups.add(manager_group)

        #additional demo users (for testing):

        if not User.objects.filter(username="d_pilot").exists():
            user = User.objects.create_user(
                username="d_pilot",
                email="d_pilot@leafroute.com",
                password="szakdoga",
                first_name="Peter",
                last_name="Pilot"
            )
            user.groups.add(driver_group)

        if not User.objects.filter(username="d_train_operator").exists():
            user = User.objects.create_user(
                username="d_train_operator",
                email="d_train_operator@leafroute.com",
                password="szakdoga",
                first_name="Thomas",
                last_name="Trainoperator"
            )
            user.groups.add(driver_group)
        
        if not User.objects.filter(username="d_driver2").exists():
            user = User.objects.create_user(
                username="d_driver2",
                email="d_driver2@leafroute.com",
                password="szakdoga",
                first_name="Jürgen",
                last_name="Bosch"
            )
            user.groups.add(driver_group)

        if not User.objects.filter(username="d_driver3").exists():
            user = User.objects.create_user(
                username="d_driver3",
                email="d_driver3@leafroute.com",
                password="szakdoga",
                first_name="Francois",
                last_name="Le Clere"
            )
            user.groups.add(driver_group)

        self.stdout.write(self.style.SUCCESS("Demo users created successfully"))
