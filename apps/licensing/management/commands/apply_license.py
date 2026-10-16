from django.core.management.base import BaseCommand
from apps.licensing.models import apply_license_key


class Command(BaseCommand):
    help = "Apply license key"

    def handle(self, *args, **kwargs):
        token = input("Paste License Key: ").strip()

        organization = apply_license_key(token)

        self.stdout.write(
            self.style.SUCCESS(f"License applied for {organization.name}")
        )
