from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

UserModel = get_user_model()

ADMIN_ID = "admin"
ADMIN_PASSWORD = "admin"


class Command(BaseCommand):

    help = "Initialize project for local development"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(self.help))

        UserModel.objects.create_superuser(ADMIN_ID, "admin@oc.drf", "admin", ADMIN_PASSWORD)

        self.stdout.write(self.style.SUCCESS("All Done !"))
