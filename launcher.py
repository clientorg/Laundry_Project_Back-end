import os
import sys
import time
import django
import platform
import threading
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")


def setup_django():
    django.setup()


def run_migrations():
    from django.core.management import call_command

    print("Checking migrations...")
    call_command("migrate", interactive=False, verbosity=0)


def load_countries():
    from django.core.management import call_command

    print("Loading countries...")
    call_command("load_countries", verbosity=0)


def check_license():
    from apps.licensing.models import AppliedLicense, apply_license_key

    license_obj = AppliedLicense.objects.filter(is_active=True).order_by("-id").first()

    if not license_obj:
        print("\nNo license found.")
        token = input("Paste Activation Key: ").strip()

        apply_license_key(token)

        print("License activated.\n")
        return

    if license_obj.expires_on < date.today():
        print("\nLicense expired.")
        token = input("Paste Renewal Key: ").strip()

        apply_license_key(token)

        print("License renewed.\n")
        return

    print("\nLicense valid.")
    print(f"Current expiry: {license_obj.expires_on}")

    choice = input(
        "Choose option: " "[1] Continue  " "[2] Upgrade / Renew Plan  : "
    ).strip()

    if choice == "2":
        token = input("Paste Upgrade / Renewal Key: ").strip()

        apply_license_key(token)

        print("Plan updated successfully.\n")
        return

    print("Continuing startup...\n")


def periodic_license_check():
    import apps.licensing.state as license_state
    from apps.licensing.models import AppliedLicense

    while True:
        try:
            license_obj = (
                AppliedLicense.objects.filter(is_active=True).order_by("-id").first()
            )

            if not license_obj:
                license_state.LICENSE_VALID = False

            elif license_obj.expires_on < date.today():
                license_state.LICENSE_VALID = False

            else:
                license_state.LICENSE_VALID = True

        except Exception:
            license_state.LICENSE_VALID = False

        time.sleep(300)


def prepare():
    system = platform.system()
    print(f"Running on {system}")

    setup_django()

    run_migrations()
    load_countries()
    check_license()


def run_server():
    setup_django()

    from waitress import serve
    from core.wsgi import application

    print("Starting backend on http://127.0.0.1:8000")

    threading.Thread(
        target=periodic_license_check,
        daemon=True,
    ).start()

    serve(application, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"

    if mode == "check":
        prepare()

    elif mode == "run":
        run_server()

    else:
        print("Usage: launcher [check|run]")
