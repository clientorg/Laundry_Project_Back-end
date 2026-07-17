import base64
from pathlib import Path

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding

CERT_DIR = Path("/opt/qz-certificates")


@extend_schema(tags=["QZ"])
class QZCertificateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        with open(CERT_DIR / "qz-public.crt", "r") as f:
            return Response(f.read())


@extend_schema(tags=["QZ"])
class QZSignView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.get("data")

        with open(CERT_DIR / "qz-private.key", "rb") as key_file:
            private_key = load_pem_private_key(key_file.read(), password=None)

        signature = private_key.sign(data.encode(), padding.PKCS1v15(), hashes.SHA512())

        return Response({"signature": base64.b64encode(signature).decode()})
