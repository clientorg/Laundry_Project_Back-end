from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.master.models import Country


class Command(BaseCommand):
    help = "Load countries from JSON file into the Country model"

    def handle(self, *args, **kwargs):
        if Country.objects.exists():
            return

        call_command(
            "loaddata",
            "countries",
            verbosity=0,
        )
        self.stdout.write(self.style.SUCCESS("Countries loaded successfully!"))
