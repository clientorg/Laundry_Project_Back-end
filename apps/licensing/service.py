# apps/licenses/services.py

import base64
import json
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

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
