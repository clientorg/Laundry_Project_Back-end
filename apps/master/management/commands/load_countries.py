from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load countries from JSON file into the Country model"

    def handle(self, *args, **kwargs):
        call_command("loaddata", "countries")
        self.stdout.write(self.style.SUCCESS("Countries loaded successfully!"))
