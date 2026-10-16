import json
import base64
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


BASE_DIR = Path(__file__).resolve().parents[2]
PUBLIC_KEY_FILE = BASE_DIR / "license_keys" / "public.pem"


def verify_license(token: str) -> dict:
    """
    Verify signed license token and return payload.
    Raises exception if invalid.
    """
    data_b64, sig_b64 = token.split(".")

    data = base64.urlsafe_b64decode(data_b64)
    signature = base64.urlsafe_b64decode(sig_b64)

    with open(PUBLIC_KEY_FILE, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    public_key.verify(
        signature,
        data,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )

    return json.loads(data.decode())
