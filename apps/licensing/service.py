# apps/licenses/services.py

import base64
import json
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from .models import License

CERT_DIR = Path("/etc/keys")
PRIVATE_KEY_FILE = CERT_DIR / "private.pem"


def load_private_key():
    with open(PRIVATE_KEY_FILE, "rb") as file:
        return serialization.load_pem_private_key(
            file.read(),
            password=None,
        )


def sign_payload(payload):
    private_key = load_private_key()

    data = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )

    return (
        base64.urlsafe_b64encode(data).decode()
        + "."
        + base64.urlsafe_b64encode(signature).decode()
    )


def generate_license_key(instance):
    payload = {
        "type": instance.license_type,
        "license_id": instance.license_id,
        "company_name": instance.company_name,
        "plan_name": instance.plan_name,
        "price": float(instance.price),
        "max_branches": instance.max_branches,
        "max_users": instance.max_users,
        "duration_days": instance.duration_days,
        "expires_on": instance.expires_on.isoformat(),
    }

    if instance.license_type == License.ACTIVATION:
        payload.update(
            {
                "admin_username": instance.admin_username,
                "admin_name": instance.admin_name,
                "admin_email": instance.admin_email,
                "admin_password": instance.admin_password,
            }
        )

    return sign_payload(payload)
