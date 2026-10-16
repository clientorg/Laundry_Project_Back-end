import base64
from pathlib import Path
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding

# Use the self-signed certificate for testing
CERT_DIR = Path("/etc/qz")


@extend_schema(tags=["QZ"])
class QZCertificateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        with open(CERT_DIR / "digital-certificate.txt", "r", encoding="utf-8") as f:
            return HttpResponse(f.read(), content_type="text/plain")


@extend_schema(tags=["QZ"])
class QZSignView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data_to_sign = request.data.get("dataToSign")
        if not data_to_sign:
            return HttpResponse("dataToSign is required", status=400)

        with open(CERT_DIR / "private-key.pem", "rb") as key_file:
            private_key = load_pem_private_key(key_file.read(), password=None)

        signature = private_key.sign(
            data_to_sign.encode(),
            padding.PKCS1v15(),
            hashes.SHA512(),
        )

        return HttpResponse(
            base64.b64encode(signature).decode(),
            content_type="text/plain",
        )
